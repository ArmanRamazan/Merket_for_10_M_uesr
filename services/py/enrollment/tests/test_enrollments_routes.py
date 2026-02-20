import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, ConflictError, ForbiddenError
from common.security import create_access_token
from app.domain.enrollment import Enrollment, EnrollmentStatus
from app.routes.enrollments import router
from app.services.enrollment_service import EnrollmentService


@pytest.fixture
def mock_service():
    return AsyncMock(spec=EnrollmentService)


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
    main_module._enrollment_service = mock_service

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
def teacher_token():
    return create_access_token(
        str(uuid4()), "test-secret",
        extra_claims={"role": "teacher", "is_verified": True},
    )


@pytest.fixture
def course_id():
    return uuid4()


@pytest.fixture
def sample_enrollment(student_id, course_id):
    return Enrollment(
        id=uuid4(),
        student_id=student_id,
        course_id=course_id,
        payment_id=None,
        status=EnrollmentStatus.ENROLLED,
        enrolled_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_enrollment_success(client, mock_service, sample_enrollment, student_token, course_id):
    mock_service.enroll.return_value = sample_enrollment

    resp = await client.post("/enrollments", json={
        "course_id": str(course_id),
    }, headers={"Authorization": f"Bearer {student_token}"})

    assert resp.status_code == 201
    assert resp.json()["course_id"] == str(sample_enrollment.course_id)


@pytest.mark.asyncio
async def test_create_enrollment_duplicate_conflict(client, mock_service, student_token, course_id):
    mock_service.enroll.side_effect = ConflictError("Already enrolled in this course")

    resp = await client.post("/enrollments", json={
        "course_id": str(course_id),
    }, headers={"Authorization": f"Bearer {student_token}"})

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_create_enrollment_teacher_forbidden(client, mock_service, teacher_token, course_id):
    mock_service.enroll.side_effect = ForbiddenError("Only students can enroll in courses")

    resp = await client.post("/enrollments", json={
        "course_id": str(course_id),
    }, headers={"Authorization": f"Bearer {teacher_token}"})

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_enrollment_no_auth(client):
    resp = await client.post("/enrollments", json={
        "course_id": str(uuid4()),
    })

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_my_enrollments(client, mock_service, sample_enrollment, student_token):
    mock_service.list_my.return_value = ([sample_enrollment], 1)

    resp = await client.get("/enrollments/me",
        headers={"Authorization": f"Bearer {student_token}"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


@pytest.mark.asyncio
async def test_get_course_enrollment_count(client, mock_service, course_id):
    mock_service.count_by_course.return_value = 42

    resp = await client.get(f"/enrollments/course/{course_id}/count")

    assert resp.status_code == 200
    assert resp.json()["count"] == 42
