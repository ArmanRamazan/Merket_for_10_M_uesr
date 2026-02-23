from __future__ import annotations

from datetime import datetime
from uuid import UUID

import asyncpg

from app.domain.token import RefreshToken


class TokenRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(
        self, user_id: UUID, token_hash: str, family_id: UUID, expires_at: datetime
    ) -> RefreshToken:
        row = await self._pool.fetchrow(
            """
            INSERT INTO refresh_tokens (user_id, token_hash, family_id, expires_at)
            VALUES ($1, $2, $3, $4)
            RETURNING id, user_id, token_hash, family_id, is_revoked, expires_at, created_at
            """,
            user_id, token_hash, family_id, expires_at,
        )
        return self._to_entity(row)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        row = await self._pool.fetchrow(
            """
            SELECT id, user_id, token_hash, family_id, is_revoked, expires_at, created_at
            FROM refresh_tokens WHERE token_hash = $1
            """,
            token_hash,
        )
        return self._to_entity(row) if row else None

    async def revoke_family(self, family_id: UUID) -> None:
        await self._pool.execute(
            "UPDATE refresh_tokens SET is_revoked = true WHERE family_id = $1",
            family_id,
        )

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        await self._pool.execute(
            "UPDATE refresh_tokens SET is_revoked = true WHERE user_id = $1",
            user_id,
        )

    async def delete_expired(self) -> int:
        result = await self._pool.execute(
            "DELETE FROM refresh_tokens WHERE expires_at < now()"
        )
        return int(result.split()[-1])

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> RefreshToken:
        return RefreshToken(
            id=row["id"],
            user_id=row["user_id"],
            token_hash=row["token_hash"],
            family_id=row["family_id"],
            is_revoked=row["is_revoked"],
            expires_at=row["expires_at"],
            created_at=row["created_at"],
        )
