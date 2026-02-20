from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import asyncpg

from app.domain.course import Course, CourseLevel

_COLUMNS = "id, teacher_id, title, description, is_free, price, duration_minutes, level, created_at, avg_rating, review_count"


class CourseRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(
        self,
        teacher_id: UUID,
        title: str,
        description: str,
        is_free: bool,
        price: Decimal | None,
        duration_minutes: int,
        level: CourseLevel,
    ) -> Course:
        row = await self._pool.fetchrow(
            f"""
            INSERT INTO courses (teacher_id, title, description, is_free, price, duration_minutes, level)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING {_COLUMNS}
            """,
            teacher_id,
            title,
            description,
            is_free,
            price,
            duration_minutes,
            level,
        )
        return self._to_entity(row)

    async def get_by_id(self, course_id: UUID) -> Course | None:
        row = await self._pool.fetchrow(
            f"SELECT {_COLUMNS} FROM courses WHERE id = $1",
            course_id,
        )
        return self._to_entity(row) if row else None

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[Course], int]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT {_COLUMNS} FROM courses ORDER BY created_at DESC LIMIT $1 OFFSET $2",
                limit,
                offset,
            )
            count = await conn.fetchval("SELECT count(*) FROM courses")
        return [self._to_entity(r) for r in rows], count

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> tuple[list[Course], int]:
        """Intentionally uses ILIKE without index — bottleneck for load testing."""
        async with self._pool.acquire() as conn:
            pattern = f"%{query}%"
            rows = await conn.fetch(
                f"""
                SELECT {_COLUMNS} FROM courses
                WHERE title ILIKE $1 OR description ILIKE $1
                ORDER BY created_at DESC LIMIT $2 OFFSET $3
                """,
                pattern,
                limit,
                offset,
            )
            count = await conn.fetchval(
                "SELECT count(*) FROM courses WHERE title ILIKE $1 OR description ILIKE $1",
                pattern,
            )
        return [self._to_entity(r) for r in rows], count

    async def list_by_teacher(
        self, teacher_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[Course], int]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT {_COLUMNS} FROM courses WHERE teacher_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
                teacher_id,
                limit,
                offset,
            )
            count = await conn.fetchval(
                "SELECT count(*) FROM courses WHERE teacher_id = $1",
                teacher_id,
            )
        return [self._to_entity(r) for r in rows], count

    async def update(self, course_id: UUID, **fields: object) -> Course | None:
        sets: list[str] = []
        values: list[object] = []
        idx = 1
        for key, val in fields.items():
            sets.append(f"{key} = ${idx}")
            values.append(val)
            idx += 1
        if not sets:
            return await self.get_by_id(course_id)
        values.append(course_id)
        row = await self._pool.fetchrow(
            f"UPDATE courses SET {', '.join(sets)} WHERE id = ${idx} RETURNING {_COLUMNS}",
            *values,
        )
        return self._to_entity(row) if row else None

    async def update_rating(
        self, course_id: UUID, avg_rating: Decimal | None, review_count: int
    ) -> None:
        await self._pool.execute(
            "UPDATE courses SET avg_rating = $1, review_count = $2 WHERE id = $3",
            avg_rating,
            review_count,
            course_id,
        )

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> Course:
        return Course(
            id=row["id"],
            teacher_id=row["teacher_id"],
            title=row["title"],
            description=row["description"],
            is_free=row["is_free"],
            price=row["price"],
            duration_minutes=row["duration_minutes"],
            level=CourseLevel(row["level"]),
            created_at=row["created_at"],
            avg_rating=row["avg_rating"],
            review_count=row["review_count"],
        )
