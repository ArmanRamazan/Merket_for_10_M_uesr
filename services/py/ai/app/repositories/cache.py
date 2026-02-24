import json
import logging
from uuid import UUID

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class AICache:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get_quiz(self, lesson_id: UUID) -> str | None:
        return await self._get(f"ai:quiz:{lesson_id}")

    async def set_quiz(self, lesson_id: UUID, data: str, ttl: int) -> None:
        await self._set(f"ai:quiz:{lesson_id}", data, ttl)

    async def get_summary(self, lesson_id: UUID) -> str | None:
        return await self._get(f"ai:summary:{lesson_id}")

    async def set_summary(self, lesson_id: UUID, data: str, ttl: int) -> None:
        await self._set(f"ai:summary:{lesson_id}", data, ttl)

    async def _get(self, key: str) -> str | None:
        try:
            val = await self._redis.get(key)
            return val.decode() if isinstance(val, bytes) else val
        except Exception:
            logger.warning("Cache read failed for %s", key)
            return None

    async def _set(self, key: str, data: str, ttl: int) -> None:
        try:
            await self._redis.set(key, data, ex=ttl)
        except Exception:
            logger.warning("Cache write failed for %s", key)
