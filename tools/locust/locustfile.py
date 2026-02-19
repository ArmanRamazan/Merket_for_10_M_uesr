import os
import random

from locust import HttpUser, task, between, events

IDENTITY_URL = os.environ.get("IDENTITY_URL", "http://localhost:8001")
COURSE_URL = os.environ.get("COURSE_URL", "http://localhost:8002")

SEARCH_TERMS = [
    "python", "javascript", "machine learning", "data science", "web",
    "mobile", "devops", "cloud", "security", "algorithms",
    "complete", "advanced", "practical", "beginner", "professional",
]

_user_counter = 0


def _next_user_id() -> int:
    global _user_counter
    _user_counter += 1
    return _user_counter


class StudentUser(HttpUser):
    """70% of traffic — browse courses, view details."""

    weight = 7
    wait_time = between(1, 3)
    host = COURSE_URL

    @task(5)
    def list_courses(self) -> None:
        offset = random.randint(0, 1000)
        self.client.get(f"/courses?limit=20&offset={offset}", name="/courses")

    @task(3)
    def view_course(self) -> None:
        resp = self.client.get("/courses?limit=1", name="/courses (for id)")
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                cid = items[0]["id"]
                self.client.get(f"/courses/{cid}", name="/courses/:id")


class SearchUser(HttpUser):
    """20% of traffic — search courses (intentional bottleneck)."""

    weight = 2
    wait_time = between(1, 2)
    host = COURSE_URL

    @task
    def search_courses(self) -> None:
        term = random.choice(SEARCH_TERMS)
        self.client.get(f"/courses?q={term}&limit=20", name="/courses?q=:term")


class TeacherUser(HttpUser):
    """10% of traffic — register as teacher, create courses."""

    weight = 1
    wait_time = between(2, 5)
    host = IDENTITY_URL

    def on_start(self) -> None:
        # Login as a pre-seeded verified teacher
        uid = random.randint(0, 6999)  # first 7000 users are verified teachers (10000 teachers * 0.7)
        email = f"user{uid}@example.com"
        password = "password123"

        resp = self.client.post(
            "/login",
            json={"email": email, "password": password},
            name="/login",
        )

        if resp.status_code == 200:
            self._token = resp.json()["access_token"]
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
    def create_course(self) -> None:
        if not self._token:
            return
        levels = ["beginner", "intermediate", "advanced"]
        is_free = random.random() < 0.3
        with self.client.post(
            f"{COURSE_URL}/courses",
            json={
                "title": f"Load Test Course {random.randint(1, 100000)}",
                "description": "Created during load testing",
                "is_free": is_free,
                "price": None if is_free else round(random.uniform(10, 199), 2),
                "duration_minutes": random.choice([60, 120, 180]),
                "level": random.choice(levels),
            },
            headers={"Authorization": f"Bearer {self._token}"},
            name="[course] POST /courses",
            catch_response=True,
        ) as resp:
            if resp.status_code == 201:
                resp.success()
            else:
                resp.failure(f"Status {resp.status_code}")
