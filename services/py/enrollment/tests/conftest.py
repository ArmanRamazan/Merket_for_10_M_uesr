import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from app.domain.enrollment import Enrollment, EnrollmentStatus
from app.repositories.enrollment_repo import EnrollmentRepository
from app.services.enrollment_service import EnrollmentService


@pytest.fixture
def enrollment_id():
    return uuid4()


@pytest.fixture
def student_id():
    return uuid4()


@pytest.fixture
def course_id():
    return uuid4()


@pytest.fixture
def sample_enrollment(enrollment_id, student_id, course_id):
    return Enrollment(
        id=enrollment_id,
        student_id=student_id,
        course_id=course_id,
        payment_id=None,
        status=EnrollmentStatus.ENROLLED,
        enrolled_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=EnrollmentRepository)


@pytest.fixture
def enrollment_service(mock_repo):
    return EnrollmentService(repo=mock_repo)
