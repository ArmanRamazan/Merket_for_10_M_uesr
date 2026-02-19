import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import bcrypt as _bcrypt
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, ConflictError, NotFoundError
from common.security import create_access_token
from app.domain.user import User
from app.routes.auth import router
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
def user_id():
    return uuid4()


@pytest.fixture
def sample_user(user_id):
    return User(
        id=user_id,
        email="test@example.com",
        password_hash=_bcrypt.hashpw(b"password123", _bcrypt.gensalt()).decode(),
        name="Test User",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def auth_token(user_id):
    return create_access_token(str(user_id), "test-secret")


@pytest.mark.asyncio
async def test_register_returns_token(client, mock_service):
    from app.domain.user import TokenPair
    mock_service.register.return_value = TokenPair(access_token="fake-jwt-token")

    resp = await client.post("/register", json={
        "email": "new@example.com",
        "password": "password123",
        "name": "New User",
    })

    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] == "fake-jwt-token"
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_returns_409(client, mock_service):
    mock_service.register.side_effect = ConflictError("Email already registered")

    resp = await client.post("/register", json={
        "email": "dup@example.com",
        "password": "password123",
        "name": "Dup",
    })

    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(client):
    resp = await client.post("/register", json={
        "email": "not-an-email",
        "password": "password123",
        "name": "Bad",
    })

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_returns_token(client, mock_service):
    from app.domain.user import TokenPair
    mock_service.authenticate.return_value = TokenPair(access_token="login-token")

    resp = await client.post("/login", json={
        "email": "test@example.com",
        "password": "password123",
    })

    assert resp.status_code == 200
    assert resp.json()["access_token"] == "login-token"


@pytest.mark.asyncio
async def test_login_wrong_creds_returns_404(client, mock_service):
    mock_service.authenticate.side_effect = NotFoundError("Invalid email or password")

    resp = await client.post("/login", json={
        "email": "test@example.com",
        "password": "wrong",
    })

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_me_returns_user(client, mock_service, sample_user, auth_token):
    mock_service.get_by_id.return_value = sample_user

    resp = await client.get("/me", headers={"Authorization": f"Bearer {auth_token}"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "test@example.com"
    assert body["name"] == "Test User"


@pytest.mark.asyncio
async def test_me_no_token_returns_422(client):
    resp = await client.get("/me")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_me_invalid_token_returns_401(client):
    resp = await client.get("/me", headers={"Authorization": "Bearer invalid-token"})
    assert resp.status_code == 401
