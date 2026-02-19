import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from app.domain.course import Course, CourseLevel
from app.repositories.course_repo import CourseRepository
from app.services.course_service import CourseService


@pytest.fixture
def course_id():
    return uuid4()


@pytest.fixture
def teacher_id():
    return uuid4()


@pytest.fixture
def sample_course(course_id, teacher_id):
    return Course(
        id=course_id,
        teacher_id=teacher_id,
        title="Python для начинающих",
        description="Базовый курс по Python",
        is_free=True,
        price=None,
        duration_minutes=120,
        level=CourseLevel.BEGINNER,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def paid_course(course_id, teacher_id):
    return Course(
        id=course_id,
        teacher_id=teacher_id,
        title="Advanced Machine Learning",
        description="Deep dive into ML",
        is_free=False,
        price=Decimal("49.99"),
        duration_minutes=600,
        level=CourseLevel.ADVANCED,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=CourseRepository)


@pytest.fixture
def course_service(mock_repo):
    return CourseService(repo=mock_repo)
