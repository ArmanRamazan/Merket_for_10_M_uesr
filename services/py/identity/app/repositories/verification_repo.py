from __future__ import annotations

from datetime import datetime
from uuid import UUID

import asyncpg

from app.domain.verification import EmailVerificationToken


class VerificationRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(
        self, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> EmailVerificationToken:
        row = await self._pool.fetchrow(
            """
            INSERT INTO email_verification_tokens (user_id, token_hash, expires_at)
            VALUES ($1, $2, $3)
            RETURNING id, user_id, token_hash, expires_at, used_at, created_at
            """,
            user_id, token_hash, expires_at,
        )
        return self._to_entity(row)

    async def get_by_hash(self, token_hash: str) -> EmailVerificationToken | None:
        row = await self._pool.fetchrow(
            """
            SELECT id, user_id, token_hash, expires_at, used_at, created_at
            FROM email_verification_tokens WHERE token_hash = $1
            """,
            token_hash,
        )
        return self._to_entity(row) if row else None

    async def mark_used(self, token_id: UUID) -> None:
        await self._pool.execute(
            "UPDATE email_verification_tokens SET used_at = now() WHERE id = $1",
            token_id,
        )

    async def delete_for_user(self, user_id: UUID) -> None:
        await self._pool.execute(
            "DELETE FROM email_verification_tokens WHERE user_id = $1",
            user_id,
        )

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> EmailVerificationToken:
        return EmailVerificationToken(
            id=row["id"],
            user_id=row["user_id"],
            token_hash=row["token_hash"],
            expires_at=row["expires_at"],
            used_at=row["used_at"],
            created_at=row["created_at"],
        )
