import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from app.domain.course import Course, CourseLevel
from app.domain.module import Module
from app.domain.lesson import Lesson
from app.domain.review import Review
from app.repositories.course_repo import CourseRepository
from app.repositories.module_repo import ModuleRepository
from app.repositories.lesson_repo import LessonRepository
from app.repositories.review_repo import ReviewRepository
from app.services.course_service import CourseService
from app.services.module_service import ModuleService
from app.services.lesson_service import LessonService
from app.services.review_service import ReviewService


@pytest.fixture
def course_id():
    return uuid4()


@pytest.fixture
def teacher_id():
    return uuid4()


@pytest.fixture
def student_id():
    return uuid4()


@pytest.fixture
def module_id():
    return uuid4()


@pytest.fixture
def lesson_id():
    return uuid4()


@pytest.fixture
def review_id():
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
def sample_module(module_id, course_id):
    return Module(
        id=module_id,
        course_id=course_id,
        title="Введение",
        order=0,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_lesson(lesson_id, module_id):
    return Lesson(
        id=lesson_id,
        module_id=module_id,
        title="Первый урок",
        content="Содержимое урока",
        video_url=None,
        duration_minutes=30,
        order=0,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_review(review_id, student_id, course_id):
    return Review(
        id=review_id,
        student_id=student_id,
        course_id=course_id,
        rating=5,
        comment="Отличный курс!",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=CourseRepository)


@pytest.fixture
def mock_module_repo():
    return AsyncMock(spec=ModuleRepository)


@pytest.fixture
def mock_lesson_repo():
    return AsyncMock(spec=LessonRepository)


@pytest.fixture
def mock_review_repo():
    return AsyncMock(spec=ReviewRepository)


@pytest.fixture
def course_service(mock_repo, mock_module_repo, mock_lesson_repo):
    return CourseService(repo=mock_repo, module_repo=mock_module_repo, lesson_repo=mock_lesson_repo)


@pytest.fixture
def module_service(mock_module_repo, mock_repo):
    return ModuleService(repo=mock_module_repo, course_repo=mock_repo)


@pytest.fixture
def lesson_service(mock_lesson_repo, mock_module_repo, mock_repo):
    return LessonService(repo=mock_lesson_repo, module_repo=mock_module_repo, course_repo=mock_repo)


@pytest.fixture
def review_service(mock_review_repo, mock_repo):
    return ReviewService(repo=mock_review_repo, course_repo=mock_repo)
