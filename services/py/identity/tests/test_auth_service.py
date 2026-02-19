import pytest
from unittest.mock import AsyncMock

import jwt

from common.errors import ConflictError, NotFoundError
from app.domain.user import User
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_success(auth_service: AuthService, mock_repo: AsyncMock, sample_user: User):
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = sample_user

    result = await auth_service.register("new@example.com", "password123", "New User")

    assert result.access_token
    assert result.token_type == "bearer"
    mock_repo.get_by_email.assert_called_once_with("new@example.com")
    mock_repo.create.assert_called_once()

    payload = jwt.decode(result.access_token, "test-secret", algorithms=["HS256"])
    assert payload["sub"] == str(sample_user.id)


@pytest.mark.asyncio
async def test_register_duplicate_email(auth_service: AuthService, mock_repo: AsyncMock, sample_user: User):
    mock_repo.get_by_email.return_value = sample_user

    with pytest.raises(ConflictError, match="Email already registered"):
        await auth_service.register("test@example.com", "password123", "Test")

    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_success(auth_service: AuthService, mock_repo: AsyncMock, sample_user: User):
    mock_repo.get_by_email.return_value = sample_user

    result = await auth_service.authenticate("test@example.com", "password123")

    assert result.access_token
    payload = jwt.decode(result.access_token, "test-secret", algorithms=["HS256"])
    assert payload["sub"] == str(sample_user.id)


@pytest.mark.asyncio
async def test_authenticate_wrong_password(auth_service: AuthService, mock_repo: AsyncMock, sample_user: User):
    mock_repo.get_by_email.return_value = sample_user

    with pytest.raises(NotFoundError, match="Invalid email or password"):
        await auth_service.authenticate("test@example.com", "wrong-password")


@pytest.mark.asyncio
async def test_authenticate_nonexistent_email(auth_service: AuthService, mock_repo: AsyncMock):
    mock_repo.get_by_email.return_value = None

    with pytest.raises(NotFoundError, match="Invalid email or password"):
        await auth_service.authenticate("nobody@example.com", "password123")


@pytest.mark.asyncio
async def test_get_by_id_success(auth_service: AuthService, mock_repo: AsyncMock, sample_user: User):
    mock_repo.get_by_id.return_value = sample_user

    result = await auth_service.get_by_id(sample_user.id)

    assert result.id == sample_user.id
    assert result.email == sample_user.email
    mock_repo.get_by_id.assert_called_once_with(sample_user.id)


@pytest.mark.asyncio
async def test_get_by_id_not_found(auth_service: AuthService, mock_repo: AsyncMock, user_id):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError, match="User not found"):
        await auth_service.get_by_id(user_id)
