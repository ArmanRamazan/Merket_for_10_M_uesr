import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, NotFoundError
from common.security import create_access_token
from app.domain.lesson import Lesson
from app.routes.lessons import router
from app.services.lesson_service import LessonService


@pytest.fixture
def mock_lesson_svc():
    return AsyncMock(spec=LessonService)


@pytest.fixture
def test_app(mock_lesson_svc):
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    import app.main as main_module
    main_module.app_settings = type("S", (), {
        "jwt_secret": "test-secret",
        "jwt_algorithm": "HS256",
    })()
    main_module._lesson_service = mock_lesson_svc

    return app


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def teacher_token():
    return create_access_token(
        str(uuid4()), "test-secret",
        extra_claims={"role": "teacher", "is_verified": True},
    )


@pytest.fixture
def module_id():
    return uuid4()


@pytest.fixture
def sample_lesson(module_id):
    return Lesson(
        id=uuid4(), module_id=module_id, title="Первый урок",
        content="Содержимое", video_url=None, duration_minutes=30,
        order=0, created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_lesson(client, mock_lesson_svc, sample_lesson, teacher_token, module_id):
    mock_lesson_svc.create.return_value = sample_lesson

    resp = await client.post(f"/modules/{module_id}/lessons", json={
        "title": "Первый урок", "content": "Содержимое",
    }, headers={"Authorization": f"Bearer {teacher_token}"})

    assert resp.status_code == 201
    assert resp.json()["title"] == "Первый урок"


@pytest.mark.asyncio
async def test_get_lesson(client, mock_lesson_svc, sample_lesson):
    mock_lesson_svc.get.return_value = sample_lesson

    resp = await client.get(f"/lessons/{sample_lesson.id}")

    assert resp.status_code == 200
    assert resp.json()["title"] == "Первый урок"


@pytest.mark.asyncio
async def test_update_lesson(client, mock_lesson_svc, sample_lesson, teacher_token):
    mock_lesson_svc.update.return_value = sample_lesson

    resp = await client.put(f"/lessons/{sample_lesson.id}", json={
        "title": "Обновлённый",
    }, headers={"Authorization": f"Bearer {teacher_token}"})

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_lesson(client, mock_lesson_svc, sample_lesson, teacher_token):
    resp = await client.delete(
        f"/lessons/{sample_lesson.id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )

    assert resp.status_code == 204
