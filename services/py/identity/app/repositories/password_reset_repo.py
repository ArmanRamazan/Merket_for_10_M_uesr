from __future__ import annotations

from datetime import datetime
from uuid import UUID

import asyncpg

from app.domain.password_reset import PasswordResetToken


class PasswordResetRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(
        self, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> PasswordResetToken:
        row = await self._pool.fetchrow(
            """
            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
            VALUES ($1, $2, $3)
            RETURNING id, user_id, token_hash, expires_at, used_at, created_at
            """,
            user_id, token_hash, expires_at,
        )
        return self._to_entity(row)

    async def get_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        row = await self._pool.fetchrow(
            """
            SELECT id, user_id, token_hash, expires_at, used_at, created_at
            FROM password_reset_tokens WHERE token_hash = $1
            """,
            token_hash,
        )
        return self._to_entity(row) if row else None

    async def mark_used(self, token_id: UUID) -> None:
        await self._pool.execute(
            "UPDATE password_reset_tokens SET used_at = now() WHERE id = $1",
            token_id,
        )

    async def delete_for_user(self, user_id: UUID) -> None:
        await self._pool.execute(
            "DELETE FROM password_reset_tokens WHERE user_id = $1",
            user_id,
        )

    async def count_recent(self, user_id: UUID, since: datetime) -> int:
        count = await self._pool.fetchval(
            "SELECT count(*) FROM password_reset_tokens WHERE user_id = $1 AND created_at >= $2",
            user_id, since,
        )
        return count

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> PasswordResetToken:
        return PasswordResetToken(
            id=row["id"],
            user_id=row["user_id"],
            token_hash=row["token_hash"],
            expires_at=row["expires_at"],
            used_at=row["used_at"],
            created_at=row["created_at"],
        )
