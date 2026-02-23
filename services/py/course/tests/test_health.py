import pytest
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.health import create_health_router


@pytest.fixture
def mock_pool():
    pool = AsyncMock()
    pool.fetchval = AsyncMock(return_value=1)
    return pool


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.ping = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def test_app(mock_pool, mock_redis):
    app = FastAPI()
    app.include_router(create_health_router(lambda: mock_pool, lambda: mock_redis))
    return app


@pytest.fixture
async def client(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as c:
        yield c


async def test_liveness(client):
    resp = await client.get("/health/live")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_readiness_healthy(client):
    resp = await client.get("/health/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["checks"]["postgres"] == "ok"
    assert data["checks"]["redis"] == "ok"


async def test_readiness_redis_down():
    pool = AsyncMock()
    pool.fetchval = AsyncMock(return_value=1)
    redis = AsyncMock()
    redis.ping = AsyncMock(side_effect=Exception("connection refused"))
    app = FastAPI()
    app.include_router(create_health_router(lambda: pool, lambda: redis))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        resp = await c.get("/health/ready")
    assert resp.status_code == 503
    assert resp.json()["checks"]["redis"] == "unavailable"
