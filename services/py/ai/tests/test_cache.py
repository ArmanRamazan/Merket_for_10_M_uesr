import json
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from app.repositories.cache import AICache


@pytest.fixture
def mock_redis():
    return AsyncMock()


@pytest.fixture
def cache(mock_redis):
    return AICache(mock_redis)


async def test_get_quiz_returns_value(cache, mock_redis):
    lesson_id = uuid4()
    mock_redis.get.return_value = b'[{"text":"q"}]'

    result = await cache.get_quiz(lesson_id)

    assert result == '[{"text":"q"}]'
    mock_redis.get.assert_called_once_with(f"ai:quiz:{lesson_id}")


async def test_get_quiz_returns_none_on_miss(cache, mock_redis):
    mock_redis.get.return_value = None

    result = await cache.get_quiz(uuid4())
    assert result is None


async def test_set_quiz(cache, mock_redis):
    lesson_id = uuid4()
    data = '[{"text":"q"}]'

    await cache.set_quiz(lesson_id, data, 3600)

    mock_redis.set.assert_called_once_with(f"ai:quiz:{lesson_id}", data, ex=3600)


async def test_get_summary_returns_value(cache, mock_redis):
    lesson_id = uuid4()
    mock_redis.get.return_value = b"Summary text"

    result = await cache.get_summary(lesson_id)

    assert result == "Summary text"
    mock_redis.get.assert_called_once_with(f"ai:summary:{lesson_id}")


async def test_set_summary(cache, mock_redis):
    lesson_id = uuid4()

    await cache.set_summary(lesson_id, "Summary", 7200)

    mock_redis.set.assert_called_once_with(f"ai:summary:{lesson_id}", "Summary", ex=7200)


async def test_get_quiz_handles_redis_error(cache, mock_redis):
    mock_redis.get.side_effect = ConnectionError("Redis down")

    result = await cache.get_quiz(uuid4())
    assert result is None


async def test_set_quiz_handles_redis_error(cache, mock_redis):
    mock_redis.set.side_effect = ConnectionError("Redis down")

    await cache.set_quiz(uuid4(), "data", 3600)
