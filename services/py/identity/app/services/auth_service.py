from uuid import UUID

import bcrypt

from common.errors import ConflictError, ForbiddenError, NotFoundError
from common.security import create_access_token
from app.domain.user import User, UserRole, TokenPair
from app.repositories.user_repo import UserRepository


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


class AuthService:
    def __init__(
        self,
        repo: UserRepository,
        jwt_secret: str,
        jwt_algorithm: str,
        jwt_ttl_seconds: int,
    ) -> None:
        self._repo = repo
        self._jwt_secret = jwt_secret
        self._jwt_algorithm = jwt_algorithm
        self._jwt_ttl_seconds = jwt_ttl_seconds

    def _create_token(self, user: User) -> str:
        return create_access_token(
            str(user.id),
            self._jwt_secret,
            self._jwt_algorithm,
            self._jwt_ttl_seconds,
            extra_claims={"role": user.role, "is_verified": user.is_verified},
        )

    async def register(self, email: str, password: str, name: str, role: UserRole = UserRole.STUDENT) -> TokenPair:
        existing = await self._repo.get_by_email(email)
        if existing:
            raise ConflictError("Email already registered")

        password_hash = _hash_password(password)
        user = await self._repo.create(email, password_hash, name, role)
        token = self._create_token(user)
        return TokenPair(access_token=token)

    async def authenticate(self, email: str, password: str) -> TokenPair:
        user = await self._repo.get_by_email(email)
        if not user or not _verify_password(password, user.password_hash):
            raise NotFoundError("Invalid email or password")

        token = self._create_token(user)
        return TokenPair(access_token=token)

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
