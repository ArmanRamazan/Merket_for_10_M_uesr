import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from common.errors import AppError, NotFoundError
from app.domain.token import RefreshToken
from app.domain.user import User, UserRole
from app.services.auth_service import AuthService, _hash_token


def _make_refresh_token(
    user_id, family_id=None, is_revoked=False, expired=False
) -> RefreshToken:
    if family_id is None:
        family_id = uuid4()
    if expired:
        expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    return RefreshToken(
        id=uuid4(),
        user_id=user_id,
        token_hash="somehash",
        family_id=family_id,
        is_revoked=is_revoked,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
    )


async def test_register_returns_refresh_token(
    auth_service: AuthService, mock_repo: AsyncMock, mock_token_repo: AsyncMock, sample_user: User
):
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = sample_user
    mock_token_repo.create.return_value = _make_refresh_token(sample_user.id)

    result = await auth_service.register("new@example.com", "password123", "New User")

    assert result.access_token
    assert result.refresh_token is not None
    mock_token_repo.create.assert_called_once()


async def test_authenticate_returns_refresh_token(
    auth_service: AuthService, mock_repo: AsyncMock, mock_token_repo: AsyncMock, sample_user: User
):
    mock_repo.get_by_email.return_value = sample_user
    mock_token_repo.create.return_value = _make_refresh_token(sample_user.id)

    result = await auth_service.authenticate("test@example.com", "password123")

    assert result.refresh_token is not None
    mock_token_repo.create.assert_called_once()


async def test_refresh_valid_token(
    auth_service: AuthService, mock_repo: AsyncMock, mock_token_repo: AsyncMock, sample_user: User
):
    family_id = uuid4()
    stored = _make_refresh_token(sample_user.id, family_id=family_id)
    mock_token_repo.get_by_hash.return_value = stored
    mock_token_repo.create.return_value = _make_refresh_token(sample_user.id, family_id=family_id)
    mock_repo.get_by_id.return_value = sample_user

    result = await auth_service.refresh("some-raw-token")

    assert result.access_token
    assert result.refresh_token is not None
    mock_token_repo.revoke_family.assert_called_once_with(family_id)


async def test_refresh_revoked_token_triggers_family_revoke(
    auth_service: AuthService, mock_token_repo: AsyncMock
):
    family_id = uuid4()
    stored = _make_refresh_token(uuid4(), family_id=family_id, is_revoked=True)
    mock_token_repo.get_by_hash.return_value = stored

    with pytest.raises(AppError, match="Token reuse detected"):
        await auth_service.refresh("some-raw-token")

    mock_token_repo.revoke_family.assert_called_once_with(family_id)


async def test_refresh_expired_token(
    auth_service: AuthService, mock_token_repo: AsyncMock
):
    stored = _make_refresh_token(uuid4(), expired=True)
    mock_token_repo.get_by_hash.return_value = stored

    with pytest.raises(AppError, match="Refresh token expired"):
        await auth_service.refresh("some-raw-token")


async def test_refresh_invalid_token(
    auth_service: AuthService, mock_token_repo: AsyncMock
):
    mock_token_repo.get_by_hash.return_value = None

    with pytest.raises(AppError, match="Invalid refresh token"):
        await auth_service.refresh("nonexistent-token")


async def test_logout_revokes_family(
    auth_service: AuthService, mock_token_repo: AsyncMock
):
    family_id = uuid4()
    stored = _make_refresh_token(uuid4(), family_id=family_id)
    mock_token_repo.get_by_hash.return_value = stored

    await auth_service.logout("some-raw-token")

    mock_token_repo.revoke_family.assert_called_once_with(family_id)


async def test_logout_with_invalid_token_does_nothing(
    auth_service: AuthService, mock_token_repo: AsyncMock
):
    mock_token_repo.get_by_hash.return_value = None

    await auth_service.logout("nonexistent-token")

    mock_token_repo.revoke_family.assert_not_called()
