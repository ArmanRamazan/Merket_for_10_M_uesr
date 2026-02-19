from uuid import UUID

import asyncpg

from app.domain.user import User


class UserRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(self, email: str, password_hash: str, name: str) -> User:
        row = await self._pool.fetchrow(
            """
            INSERT INTO users (email, password_hash, name)
            VALUES ($1, $2, $3)
            RETURNING id, email, password_hash, name, created_at
            """,
            email,
            password_hash,
            name,
        )
        return self._to_entity(row)

    async def get_by_email(self, email: str) -> User | None:
        row = await self._pool.fetchrow(
            "SELECT id, email, password_hash, name, created_at FROM users WHERE email = $1",
            email,
        )
        return self._to_entity(row) if row else None

    async def get_by_id(self, user_id: UUID) -> User | None:
        row = await self._pool.fetchrow(
            "SELECT id, email, password_hash, name, created_at FROM users WHERE id = $1",
            user_id,
        )
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> User:
        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            name=row["name"],
            created_at=row["created_at"],
        )
