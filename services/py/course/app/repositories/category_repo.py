from __future__ import annotations

from uuid import UUID

import asyncpg

from app.domain.category import Category


class CategoryRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def list_all(self) -> list[Category]:
        rows = await self._pool.fetch(
            "SELECT id, name, slug FROM categories ORDER BY name"
        )
        return [self._to_entity(r) for r in rows]

    async def get_by_id(self, category_id: UUID) -> Category | None:
        row = await self._pool.fetchrow(
            "SELECT id, name, slug FROM categories WHERE id = $1",
            category_id,
        )
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> Category:
        return Category(id=row["id"], name=row["name"], slug=row["slug"])
