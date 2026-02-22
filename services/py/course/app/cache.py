from __future__ import annotations

import json
from uuid import UUID

from redis.asyncio import Redis


class CourseCache:
    def __init__(self, redis: Redis) -> None:
        self._r = redis

    async def get_course(self, course_id: UUID) -> dict | None:
        data = await self._r.get(f"course:{course_id}")
        return json.loads(data) if data else None

    async def set_course(self, course_id: UUID, data: dict, ttl: int = 300) -> None:
        await self._r.set(f"course:{course_id}", json.dumps(data, default=str), ex=ttl)

    async def invalidate_course(self, course_id: UUID) -> None:
        await self._r.delete(f"course:{course_id}", f"curriculum:{course_id}")

    async def get_curriculum(self, course_id: UUID) -> dict | None:
        data = await self._r.get(f"curriculum:{course_id}")
        return json.loads(data) if data else None

    async def set_curriculum(self, course_id: UUID, data: dict, ttl: int = 300) -> None:
        await self._r.set(f"curriculum:{course_id}", json.dumps(data, default=str), ex=ttl)
