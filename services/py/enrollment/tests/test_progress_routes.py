import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, ConflictError, ForbiddenError
from common.security import create_access_token
from app.domain.progress import LessonProgress
from app.routes.progress import router
from app.services.progress_service import ProgressService


@pytest.fixture
def mock_progress_svc():
    return AsyncMock(spec=ProgressService)


@pytest.fixture
def test_app(mock_progress_svc):
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    import app.main as main_module
    main_module.app_settings = type("S", (), {
        "jwt_secret": "test-secret",
        "jwt_algorithm": "HS256",
    })()
    main_module._progress_service = mock_progress_svc

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
def lesson_id():
    return uuid4()


@pytest.fixture
def course_id():
    return uuid4()


@pytest.fixture
def sample_progress(student_id, lesson_id, course_id):
    return LessonProgress(
        id=uuid4(), student_id=student_id, lesson_id=lesson_id,
        course_id=course_id, completed_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_complete_lesson(client, mock_progress_svc, sample_progress, student_token, lesson_id, course_id):
    mock_progress_svc.complete_lesson.return_value = sample_progress

    resp = await client.post(f"/progress/lessons/{lesson_id}/complete", json={
        "course_id": str(course_id),
    }, headers={"Authorization": f"Bearer {student_token}"})

    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_get_course_progress(client, mock_progress_svc, student_token, course_id):
    mock_progress_svc.get_course_progress.return_value = {
        "course_id": course_id,
        "completed_lessons": 3,
        "total_lessons": 10,
        "percentage": 30.0,
    }

    resp = await client.get(
        f"/progress/courses/{course_id}?total_lessons=10",
        headers={"Authorization": f"Bearer {student_token}"},
    )

    assert resp.status_code == 200
    assert resp.json()["percentage"] == 30.0


@pytest.mark.asyncio
async def test_list_completed_lessons(client, mock_progress_svc, student_token, course_id, lesson_id):
    mock_progress_svc.list_completed_lessons.return_value = [lesson_id]

    resp = await client.get(
        f"/progress/courses/{course_id}/lessons",
        headers={"Authorization": f"Bearer {student_token}"},
    )

    assert resp.status_code == 200
    assert len(resp.json()["completed_lesson_ids"]) == 1
