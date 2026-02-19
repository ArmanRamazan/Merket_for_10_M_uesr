import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import bcrypt

from app.domain.user import User, UserRole
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def sample_user(user_id):
    return User(
        id=user_id,
        email="test@example.com",
        password_hash=bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode(),
        name="Test User",
        role=UserRole.STUDENT,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def teacher_user(user_id):
    return User(
        id=user_id,
        email="teacher@example.com",
        password_hash=bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode(),
        name="Test Teacher",
        role=UserRole.TEACHER,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def auth_service(mock_repo):
    return AuthService(
        repo=mock_repo,
        jwt_secret="test-secret",
        jwt_algorithm="HS256",
        jwt_ttl_seconds=3600,
    )
