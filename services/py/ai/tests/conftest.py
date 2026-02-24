import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("GEMINI_API_KEY", "test-api-key")

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.config import Settings
from app.repositories.llm_client import GeminiClient
from app.repositories.cache import AICache
from app.services.ai_service import AIService


@pytest.fixture
def lesson_id():
    return uuid4()


@pytest.fixture
def lesson_content():
    return "Python is a high-level programming language known for its simplicity and readability."


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def mock_llm():
    mock = AsyncMock(spec=GeminiClient)
    mock.model_name = "gemini-2.0-flash-lite"
    return mock


@pytest.fixture
def mock_cache():
    return AsyncMock(spec=AICache)


@pytest.fixture
def ai_service(mock_llm, mock_cache, settings):
    return AIService(llm=mock_llm, cache=mock_cache, settings=settings)
