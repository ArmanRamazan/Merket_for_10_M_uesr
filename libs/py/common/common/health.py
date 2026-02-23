from __future__ import annotations

from typing import Callable

from fastapi import APIRouter
from fastapi.responses import JSONResponse


def create_health_router(
    pool_getter: Callable,
    redis_getter: Callable | None = None,
) -> APIRouter:
    router = APIRouter(tags=["health"])

    @router.get("/health/live")
    async def liveness() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/health/ready")
    async def readiness() -> JSONResponse:
        checks: dict[str, str] = {}
        healthy = True

        pool = pool_getter()
        try:
            await pool.fetchval("SELECT 1")
            checks["postgres"] = "ok"
        except Exception:
            checks["postgres"] = "unavailable"
            healthy = False

        if redis_getter is not None:
            redis = redis_getter()
            if redis is not None:
                try:
                    await redis.ping()
                    checks["redis"] = "ok"
                except Exception:
                    checks["redis"] = "unavailable"
                    healthy = False

        status_code = 200 if healthy else 503
        return JSONResponse(
            content={"status": "ok" if healthy else "degraded", "checks": checks},
            status_code=status_code,
        )

    return router
