import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, ForbiddenError, NotFoundError
from common.security import create_access_token
from app.domain.module import Module
from app.routes.modules import router
from app.services.module_service import ModuleService


@pytest.fixture
def mock_module_svc():
    return AsyncMock(spec=ModuleService)


@pytest.fixture
def test_app(mock_module_svc):
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    import app.main as main_module
    main_module.app_settings = type("S", (), {
        "jwt_secret": "test-secret",
        "jwt_algorithm": "HS256",
    })()
    main_module._module_service = mock_module_svc

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
def course_id():
    return uuid4()


@pytest.fixture
def sample_module(course_id):
    return Module(
        id=uuid4(), course_id=course_id, title="Введение",
        order=0, created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_module(client, mock_module_svc, sample_module, teacher_token, course_id):
    mock_module_svc.create.return_value = sample_module

    resp = await client.post(f"/courses/{course_id}/modules", json={
        "title": "Введение", "order": 0,
    }, headers={"Authorization": f"Bearer {teacher_token}"})

    assert resp.status_code == 201
    assert resp.json()["title"] == "Введение"


@pytest.mark.asyncio
async def test_update_module(client, mock_module_svc, sample_module, teacher_token):
    mock_module_svc.update.return_value = sample_module

    resp = await client.put(f"/modules/{sample_module.id}", json={
        "title": "Обновлённый модуль",
    }, headers={"Authorization": f"Bearer {teacher_token}"})

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_module(client, mock_module_svc, sample_module, teacher_token):
    resp = await client.delete(
        f"/modules/{sample_module.id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )

    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_create_module_no_auth(client, course_id):
    resp = await client.post(f"/courses/{course_id}/modules", json={
        "title": "Test",
    })

    assert resp.status_code == 422
