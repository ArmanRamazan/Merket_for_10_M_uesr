import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import bcrypt as _bcrypt
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, ForbiddenError, NotFoundError
from common.security import create_access_token
from app.domain.user import User, UserRole
from app.routes.admin import router
from app.services.auth_service import AuthService


@pytest.fixture
def mock_service():
    return AsyncMock(spec=AuthService)


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
    main_module._auth_service = mock_service

    return app


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def unverified_teacher():
    return User(
        id=uuid4(),
        email="unverified@example.com",
        password_hash=_bcrypt.hashpw(b"password123", _bcrypt.gensalt()).decode(),
        name="Unverified Teacher",
        role=UserRole.TEACHER,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def admin_token():
    return create_access_token(
        str(uuid4()), "test-secret",
        extra_claims={"role": "admin", "is_verified": True},
    )


@pytest.fixture
def student_token():
    return create_access_token(
        str(uuid4()), "test-secret",
        extra_claims={"role": "student", "is_verified": False},
    )


@pytest.mark.asyncio
async def test_list_pending_success(client, mock_service, admin_token, unverified_teacher):
    mock_service.list_pending_teachers.return_value = ([unverified_teacher], 1)

    resp = await client.get(
        "/admin/teachers/pending",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["email"] == "unverified@example.com"


@pytest.mark.asyncio
async def test_list_pending_no_auth(client):
    resp = await client.get("/admin/teachers/pending")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_pending_forbidden(client, mock_service, student_token):
    mock_service.list_pending_teachers.side_effect = ForbiddenError("Admin access required")

    resp = await client.get(
        "/admin/teachers/pending",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_verify_success(client, mock_service, admin_token, unverified_teacher):
    verified = User(
        id=unverified_teacher.id,
        email=unverified_teacher.email,
        password_hash=unverified_teacher.password_hash,
        name=unverified_teacher.name,
        role=UserRole.TEACHER,
        is_verified=True,
        created_at=unverified_teacher.created_at,
    )
    mock_service.verify_teacher.return_value = verified

    resp = await client.patch(
        f"/admin/users/{unverified_teacher.id}/verify",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_verify_not_found(client, mock_service, admin_token):
    mock_service.verify_teacher.side_effect = NotFoundError("User not found")

    resp = await client.patch(
        "/admin/users/00000000-0000-0000-0000-000000000000/verify",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404
