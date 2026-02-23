import pytest
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from common.rate_limit import RateLimiter, RateLimitMiddleware


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.incr = AsyncMock(side_effect=lambda key: _counter(key))
    redis.expire = AsyncMock()
    return redis


_counters: dict[str, int] = {}


def _counter(key: str) -> int:
    _counters[key] = _counters.get(key, 0) + 1
    return _counters[key]


@pytest.fixture(autouse=True)
def reset_counters():
    _counters.clear()


async def test_rate_limiter_allows_under_limit(mock_redis):
    limiter = RateLimiter(mock_redis, limit=3, window_seconds=60)
    assert await limiter.check("test-ip") is True
    assert await limiter.check("test-ip") is True
    assert await limiter.check("test-ip") is True


async def test_rate_limiter_blocks_over_limit(mock_redis):
    limiter = RateLimiter(mock_redis, limit=2, window_seconds=60)
    assert await limiter.check("test-ip") is True
    assert await limiter.check("test-ip") is True
    assert await limiter.check("test-ip") is False


async def test_rate_limit_middleware_returns_429():
    call_count = 0

    async def mock_incr(key: str) -> int:
        nonlocal call_count
        call_count += 1
        return call_count

    redis = AsyncMock()
    redis.incr = mock_incr
    redis.expire = AsyncMock()

    test_app = FastAPI()
    test_app.add_middleware(RateLimitMiddleware, redis_getter=lambda: redis, limit=2, window=60)

    @test_app.get("/test")
    async def test_endpoint() -> dict[str, str]:
        return {"ok": "true"}

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        resp1 = await client.get("/test")
        assert resp1.status_code == 200
        resp2 = await client.get("/test")
        assert resp2.status_code == 200
        resp3 = await client.get("/test")
        assert resp3.status_code == 429
        assert resp3.json()["detail"] == "Too many requests"
        assert "Retry-After" in resp3.headers
