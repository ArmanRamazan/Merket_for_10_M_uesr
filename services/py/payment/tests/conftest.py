import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from app.domain.payment import Payment, PaymentStatus
from app.repositories.payment_repo import PaymentRepository
from app.services.payment_service import PaymentService


@pytest.fixture
def payment_id():
    return uuid4()


@pytest.fixture
def student_id():
    return uuid4()


@pytest.fixture
def course_id():
    return uuid4()


@pytest.fixture
def sample_payment(payment_id, student_id, course_id):
    return Payment(
        id=payment_id,
        student_id=student_id,
        course_id=course_id,
        amount=Decimal("49.99"),
        status=PaymentStatus.COMPLETED,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=PaymentRepository)


@pytest.fixture
def payment_service(mock_repo):
    return PaymentService(repo=mock_repo)
