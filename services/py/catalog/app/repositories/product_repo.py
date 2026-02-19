from __future__ import annotations

from uuid import UUID

import asyncpg

from app.domain.product import Product


class ProductRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(
        self, seller_id: UUID, title: str, description: str, price: float, stock: int
    ) -> Product:
        row = await self._pool.fetchrow(
            """
            INSERT INTO products (seller_id, title, description, price, stock)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, seller_id, title, description, price, stock, created_at
            """,
            seller_id,
            title,
            description,
            price,
            stock,
        )
        return self._to_entity(row)

    async def get_by_id(self, product_id: UUID) -> Product | None:
        row = await self._pool.fetchrow(
            "SELECT id, seller_id, title, description, price, stock, created_at FROM products WHERE id = $1",
            product_id,
        )
        return self._to_entity(row) if row else None

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[Product], int]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, seller_id, title, description, price, stock, created_at
                FROM products ORDER BY created_at DESC LIMIT $1 OFFSET $2
                """,
                limit,
                offset,
            )
            count = await conn.fetchval("SELECT count(*) FROM products")
        return [self._to_entity(r) for r in rows], count

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> tuple[list[Product], int]:
        """Intentionally uses ILIKE without index — bottleneck for load testing."""
        async with self._pool.acquire() as conn:
            pattern = f"%{query}%"
            rows = await conn.fetch(
                """
                SELECT id, seller_id, title, description, price, stock, created_at
                FROM products
                WHERE title ILIKE $1 OR description ILIKE $1
                ORDER BY created_at DESC LIMIT $2 OFFSET $3
                """,
                pattern,
                limit,
                offset,
            )
            count = await conn.fetchval(
                "SELECT count(*) FROM products WHERE title ILIKE $1 OR description ILIKE $1",
                pattern,
            )
        return [self._to_entity(r) for r in rows], count

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> Product:
        return Product(
            id=row["id"],
            seller_id=row["seller_id"],
            title=row["title"],
            description=row["description"],
            price=row["price"],
            stock=row["stock"],
            created_at=row["created_at"],
        )
