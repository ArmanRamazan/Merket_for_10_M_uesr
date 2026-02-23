from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import bcrypt

from common.errors import AppError, ConflictError, ForbiddenError, NotFoundError
from common.security import create_access_token
from app.domain.user import User, UserRole, TokenPair
from app.repositories.user_repo import UserRepository
from app.repositories.token_repo import TokenRepository


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    def __init__(
        self,
        repo: UserRepository,
        jwt_secret: str,
        jwt_algorithm: str,
        jwt_ttl_seconds: int,
        token_repo: TokenRepository | None = None,
        refresh_token_ttl_days: int = 30,
    ) -> None:
        self._repo = repo
        self._jwt_secret = jwt_secret
        self._jwt_algorithm = jwt_algorithm
        self._jwt_ttl_seconds = jwt_ttl_seconds
        self._token_repo = token_repo
        self._refresh_ttl_days = refresh_token_ttl_days

    def _create_token(self, user: User) -> str:
        return create_access_token(
            str(user.id),
            self._jwt_secret,
            self._jwt_algorithm,
            self._jwt_ttl_seconds,
            extra_claims={"role": user.role, "is_verified": user.is_verified},
        )

    async def _create_refresh_token(self, user_id: UUID, family_id: UUID | None = None) -> str:
        assert self._token_repo is not None
        raw_token = secrets.token_urlsafe(48)
        token_hash = _hash_token(raw_token)
        if family_id is None:
            family_id = uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(days=self._refresh_ttl_days)
        await self._token_repo.create(user_id, token_hash, family_id, expires_at)
        return raw_token

    async def _create_token_pair(self, user: User, family_id: UUID | None = None) -> TokenPair:
        access = self._create_token(user)
        if self._token_repo is not None:
            refresh = await self._create_refresh_token(user.id, family_id)
            return TokenPair(access_token=access, refresh_token=refresh)
        return TokenPair(access_token=access)

    async def register(self, email: str, password: str, name: str, role: UserRole = UserRole.STUDENT) -> TokenPair:
        existing = await self._repo.get_by_email(email)
        if existing:
            raise ConflictError("Email already registered")

        password_hash = _hash_password(password)
        user = await self._repo.create(email, password_hash, name, role)
        return await self._create_token_pair(user)

    async def authenticate(self, email: str, password: str) -> TokenPair:
        user = await self._repo.get_by_email(email)
        if not user or not _verify_password(password, user.password_hash):
            raise NotFoundError("Invalid email or password")

        return await self._create_token_pair(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        assert self._token_repo is not None
        token_hash = _hash_token(refresh_token)
        stored = await self._token_repo.get_by_hash(token_hash)

        if not stored:
            raise AppError("Invalid refresh token", status_code=401)

        if stored.is_revoked:
            await self._token_repo.revoke_family(stored.family_id)
            raise AppError("Token reuse detected", status_code=401)

        if stored.expires_at < datetime.now(timezone.utc):
            raise AppError("Refresh token expired", status_code=401)

        await self._token_repo.revoke_family(stored.family_id)

        user = await self._repo.get_by_id(stored.user_id)
        if not user:
            raise NotFoundError("User not found")

        return await self._create_token_pair(user, family_id=stored.family_id)

    async def logout(self, refresh_token: str) -> None:
        assert self._token_repo is not None
        token_hash = _hash_token(refresh_token)
        stored = await self._token_repo.get_by_hash(token_hash)
        if stored:
            await self._token_repo.revoke_family(stored.family_id)

    async def get_by_id(self, user_id: UUID) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def list_pending_teachers(
        self, role: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[User], int]:
        if role != UserRole.ADMIN:
            raise ForbiddenError("Admin access required")
        return await self._repo.list_unverified_teachers(limit, offset)

    async def verify_teacher(self, admin_role: str, user_id: UUID) -> User:
        if admin_role != UserRole.ADMIN:
            raise ForbiddenError("Admin access required")
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if user.role != UserRole.TEACHER:
            raise ConflictError("User is not a teacher")
        if user.is_verified:
            raise ConflictError("Teacher already verified")
        updated = await self._repo.set_verified(user_id, True)
        if not updated:
            raise NotFoundError("User not found")
        return updated
