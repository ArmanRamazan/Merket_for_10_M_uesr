import os
import random

from locust import HttpUser, task, between, events

IDENTITY_URL = os.environ.get("IDENTITY_URL", "http://localhost:8001")
CATALOG_URL = os.environ.get("CATALOG_URL", "http://localhost:8002")

SEARCH_TERMS = [
    "premium", "vintage", "modern", "classic", "wireless",
    "organic", "compact", "professional", "limited", "handmade",
    "electronics", "clothing", "sports", "beauty", "health",
]

_tokens: list[str] = []
_user_counter = 0


def _next_user_id() -> int:
    global _user_counter
    _user_counter += 1
    return _user_counter


class BrowsingUser(HttpUser):
    """70% of traffic — browse catalog, view products."""

    weight = 7
    wait_time = between(1, 3)
    host = CATALOG_URL

    @task(5)
    def list_products(self) -> None:
        offset = random.randint(0, 1000)
        self.client.get(f"/products?limit=20&offset={offset}", name="/products")

    @task(3)
    def view_product(self) -> None:
        resp = self.client.get("/products?limit=1", name="/products (for id)")
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                pid = items[0]["id"]
                self.client.get(f"/products/{pid}", name="/products/:id")


class SearchUser(HttpUser):
    """20% of traffic — search catalog (intentional bottleneck)."""

    weight = 2
    wait_time = between(1, 2)
    host = CATALOG_URL

    @task
    def search_products(self) -> None:
        term = random.choice(SEARCH_TERMS)
        self.client.get(f"/products?q={term}&limit=20", name="/products?q=:term")


class SellerUser(HttpUser):
    """10% of traffic — register, login, create products."""

    weight = 1
    wait_time = between(2, 5)
    host = IDENTITY_URL

    def on_start(self) -> None:
        uid = _next_user_id()
        email = f"locust_seller_{uid}@test.com"
        password = "testpass123"

        resp = self.client.post(
            "/register",
            json={"email": email, "password": password, "name": f"Seller {uid}"},
            name="/register",
        )

        if resp.status_code == 200:
            self._token = resp.json()["access_token"]
        elif resp.status_code == 409:
            resp = self.client.post(
                "/login",
                json={"email": email, "password": password},
                name="/login",
            )
            if resp.status_code == 200:
                self._token = resp.json()["access_token"]
            else:
                self._token = None
        else:
            self._token = None

    @task(2)
    def get_me(self) -> None:
        if not self._token:
            return
        self.client.get(
            "/me",
            headers={"Authorization": f"Bearer {self._token}"},
            name="/me",
        )

    @task(1)
    def create_product(self) -> None:
        if not self._token:
            return
        # Post to catalog service
        with self.client.post(
            f"{CATALOG_URL}/products",
            json={
                "title": f"Load Test Product {random.randint(1, 100000)}",
                "description": "Created during load testing",
                "price": round(random.uniform(10, 999), 2),
                "stock": random.randint(1, 100),
            },
            headers={"Authorization": f"Bearer {self._token}"},
            name="[catalog] POST /products",
            catch_response=True,
        ) as resp:
            if resp.status_code == 201:
                resp.success()
            else:
                resp.failure(f"Status {resp.status_code}")
