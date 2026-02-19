import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, ForbiddenError, NotFoundError
from common.security import create_access_token
from app.domain.course import Course, CourseLevel
from app.routes.courses import router
from app.services.course_service import CourseService


@pytest.fixture
def mock_service():
    return AsyncMock(spec=CourseService)


@pytest.fixture
def test_app(mock_service):
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    import app.main as main_module
    main_module.app_settings = type("S", (), {
        "jwt_secret": "test-secret",
        "jwt_algorithm": "HS256",
    })()
    main_module._course_service = mock_service

    return app


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def teacher_id():
    return uuid4()


@pytest.fixture
def teacher_token(teacher_id):
    return create_access_token(
        str(teacher_id), "test-secret",
        extra_claims={"role": "teacher", "is_verified": True},
    )


@pytest.fixture
def student_token():
    return create_access_token(
        str(uuid4()), "test-secret",
        extra_claims={"role": "student", "is_verified": False},
    )


@pytest.fixture
def unverified_teacher_token():
    return create_access_token(
        str(uuid4()), "test-secret",
        extra_claims={"role": "teacher", "is_verified": False},
    )


@pytest.fixture
def sample_course(teacher_id):
    return Course(
        id=uuid4(),
        teacher_id=teacher_id,
        title="Python для начинающих",
        description="Базовый курс",
        is_free=True,
        price=None,
        duration_minutes=120,
        level=CourseLevel.BEGINNER,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_list_courses(client, mock_service, sample_course):
    from app.domain.course import CourseListResponse, CourseResponse
    mock_service.list.return_value = ([sample_course], 1)

    resp = await client.get("/courses")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["title"] == "Python для начинающих"


@pytest.mark.asyncio
async def test_search_courses(client, mock_service, sample_course):
    mock_service.search.return_value = ([sample_course], 1)

    resp = await client.get("/courses?q=python")

    assert resp.status_code == 200
    mock_service.search.assert_called_once_with("python", 20, 0)


@pytest.mark.asyncio
async def test_get_course(client, mock_service, sample_course):
    mock_service.get.return_value = sample_course

    resp = await client.get(f"/courses/{sample_course.id}")

    assert resp.status_code == 200
    assert resp.json()["title"] == "Python для начинающих"


@pytest.mark.asyncio
async def test_get_course_not_found(client, mock_service):
    mock_service.get.side_effect = NotFoundError("Course not found")

    resp = await client.get(f"/courses/{uuid4()}")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_course_by_verified_teacher(client, mock_service, sample_course, teacher_token):
    mock_service.create.return_value = sample_course

    resp = await client.post("/courses", json={
        "title": "Python для начинающих",
        "description": "Базовый курс",
        "is_free": True,
        "duration_minutes": 120,
        "level": "beginner",
    }, headers={"Authorization": f"Bearer {teacher_token}"})

    assert resp.status_code == 201
    assert resp.json()["title"] == "Python для начинающих"


@pytest.mark.asyncio
async def test_create_course_forbidden_for_student(client, mock_service, student_token):
    mock_service.create.side_effect = ForbiddenError("Only teachers can create courses")

    resp = await client.post("/courses", json={
        "title": "Test",
    }, headers={"Authorization": f"Bearer {student_token}"})

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_course_forbidden_for_unverified_teacher(client, mock_service, unverified_teacher_token):
    mock_service.create.side_effect = ForbiddenError("Only verified teachers can create courses")

    resp = await client.post("/courses", json={
        "title": "Test",
    }, headers={"Authorization": f"Bearer {unverified_teacher_token}"})

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_course_no_auth_returns_422(client):
    resp = await client.post("/courses", json={"title": "Test"})

    assert resp.status_code == 422
