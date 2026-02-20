import os
import random

from locust import HttpUser, task, between, events

IDENTITY_URL = os.environ.get("IDENTITY_URL", "http://localhost:8001")
COURSE_URL = os.environ.get("COURSE_URL", "http://localhost:8002")
ENROLLMENT_URL = os.environ.get("ENROLLMENT_URL", "http://localhost:8003")
PAYMENT_URL = os.environ.get("PAYMENT_URL", "http://localhost:8004")

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
    """70% of traffic — browse courses, view details, enroll, view lessons, complete."""

    weight = 7
    wait_time = between(1, 3)
    host = COURSE_URL

    def on_start(self) -> None:
        uid = random.randint(10000, 49999)  # students start at index 10000
        email = f"user{uid}@example.com"
        password = "password123"

        resp = self.client.post(
            f"{IDENTITY_URL}/login",
            json={"email": email, "password": password},
            name="[identity] /login",
        )

        if resp.status_code == 200:
            self._token = resp.json()["access_token"]
        else:
            self._token = None

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

    @task(3)
    def view_curriculum(self) -> None:
        resp = self.client.get("/courses?limit=1", name="/courses (for curriculum)")
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                cid = items[0]["id"]
                self.client.get(f"/courses/{cid}/curriculum", name="/courses/:id/curriculum")

    @task(2)
    def view_lesson(self) -> None:
        resp = self.client.get("/courses?limit=1", name="/courses (for lesson)")
        if resp.status_code != 200:
            return
        items = resp.json().get("items", [])
        if not items:
            return
        cid = items[0]["id"]
        cur_resp = self.client.get(f"/courses/{cid}/curriculum", name="/courses/:id/curriculum (for lesson)")
        if cur_resp.status_code != 200:
            return
        modules = cur_resp.json().get("modules", [])
        for mod in modules:
            lessons = mod.get("lessons", [])
            if lessons:
                lid = random.choice(lessons)["id"]
                self.client.get(f"/lessons/{lid}", name="/lessons/:id")
                return

    @task(1)
    def complete_lesson(self) -> None:
        if not self._token:
            return
        resp = self.client.get("/courses?limit=1", name="/courses (for complete)")
        if resp.status_code != 200:
            return
        items = resp.json().get("items", [])
        if not items:
            return
        cid = items[0]["id"]
        cur_resp = self.client.get(f"/courses/{cid}/curriculum", name="/courses/:id/curriculum (for complete)")
        if cur_resp.status_code != 200:
            return
        modules = cur_resp.json().get("modules", [])
        for mod in modules:
            lessons = mod.get("lessons", [])
            if lessons:
                lid = random.choice(lessons)["id"]
                with self.client.post(
                    f"{ENROLLMENT_URL}/progress/lessons/{lid}/complete",
                    json={"course_id": cid},
                    headers={"Authorization": f"Bearer {self._token}"},
                    name="[enrollment] POST /progress/lessons/:id/complete",
                    catch_response=True,
                ) as r:
                    if r.status_code in (201, 409):
                        r.success()
                    else:
                        r.failure(f"Status {r.status_code}")
                return

    @task(2)
    def enroll_in_course(self) -> None:
        if not self._token:
            return
        resp = self.client.get("/courses?limit=1", name="/courses (for enroll)")
        if resp.status_code != 200:
            return
        items = resp.json().get("items", [])
        if not items:
            return
        course = items[0]
        cid = course["id"]

        if not course["is_free"] and course.get("price"):
            with self.client.post(
                f"{PAYMENT_URL}/payments",
                json={"course_id": cid, "amount": float(course["price"])},
                headers={"Authorization": f"Bearer {self._token}"},
                name="[payment] POST /payments",
                catch_response=True,
            ) as pay_resp:
                if pay_resp.status_code == 201:
                    pay_resp.success()
                else:
                    pay_resp.failure(f"Status {pay_resp.status_code}")

        with self.client.post(
            f"{ENROLLMENT_URL}/enrollments",
            json={"course_id": cid},
            headers={"Authorization": f"Bearer {self._token}"},
            name="[enrollment] POST /enrollments",
            catch_response=True,
        ) as enroll_resp:
            if enroll_resp.status_code in (201, 409):
                enroll_resp.success()
            else:
                enroll_resp.failure(f"Status {enroll_resp.status_code}")


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

    @task(1)
    def list_my_courses(self) -> None:
        if not self._token:
            return
        self.client.get(
            f"{COURSE_URL}/courses/my?limit=10",
            headers={"Authorization": f"Bearer {self._token}"},
            name="[course] /courses/my",
        )
