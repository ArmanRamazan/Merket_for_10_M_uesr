import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from app.domain.notification import Notification, NotificationType
from app.repositories.notification_repo import NotificationRepository
from app.services.notification_service import NotificationService


@pytest.fixture
def notification_id():
    return uuid4()


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def sample_notification(notification_id, user_id):
    return Notification(
        id=notification_id,
        user_id=user_id,
        type=NotificationType.ENROLLMENT,
        title="You enrolled in Python 101",
        body="Welcome to the course!",
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=NotificationRepository)


@pytest.fixture
def notification_service(mock_repo):
    return NotificationService(repo=mock_repo)
