from __future__ import annotations

from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class RateLimiter:
    def __init__(self, redis, limit: int, window_seconds: int) -> None:  # type: ignore[no-untyped-def]
        self._redis = redis
        self._limit = limit
        self._window = window_seconds

    async def check(self, key: str) -> bool:
        redis_key = f"rate:{key}"
        current = await self._redis.incr(redis_key)
        if current == 1:
            await self._redis.expire(redis_key, self._window)
        return current <= self._limit


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, redis_getter: Callable, limit: int, window: int) -> None:
        super().__init__(app)
        self._redis_getter = redis_getter
        self._limit = limit
        self._window = window

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        redis = self._redis_getter()
        if redis is None:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        limiter = RateLimiter(redis, self._limit, self._window)
        if not await limiter.check(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(self._window)},
            )
        return await call_next(request)
