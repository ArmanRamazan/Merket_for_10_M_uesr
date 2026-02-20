import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, ForbiddenError, ConflictError
from common.security import create_access_token
from app.domain.review import Review
from app.routes.reviews import router
from app.services.review_service import ReviewService


@pytest.fixture
def mock_review_svc():
    return AsyncMock(spec=ReviewService)


@pytest.fixture
def test_app(mock_review_svc):
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    import app.main as main_module
    main_module.app_settings = type("S", (), {
        "jwt_secret": "test-secret",
        "jwt_algorithm": "HS256",
    })()
    main_module._review_service = mock_review_svc

    return app


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def student_id():
    return uuid4()


@pytest.fixture
def student_token(student_id):
    return create_access_token(
        str(student_id), "test-secret",
        extra_claims={"role": "student", "is_verified": False},
    )


@pytest.fixture
def course_id():
    return uuid4()


@pytest.fixture
def sample_review(student_id, course_id):
    return Review(
        id=uuid4(), student_id=student_id, course_id=course_id,
        rating=5, comment="Отличный курс!", created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_review(client, mock_review_svc, sample_review, student_token, course_id):
    mock_review_svc.create.return_value = sample_review

    resp = await client.post("/reviews", json={
        "course_id": str(course_id), "rating": 5, "comment": "Отличный курс!",
    }, headers={"Authorization": f"Bearer {student_token}"})

    assert resp.status_code == 201
    assert resp.json()["rating"] == 5


@pytest.mark.asyncio
async def test_list_reviews(client, mock_review_svc, sample_review, course_id):
    mock_review_svc.list_by_course.return_value = ([sample_review], 1)

    resp = await client.get(f"/reviews/course/{course_id}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


@pytest.mark.asyncio
async def test_create_review_no_auth(client, course_id):
    resp = await client.post("/reviews", json={
        "course_id": str(course_id), "rating": 5,
    })

    assert resp.status_code == 422
