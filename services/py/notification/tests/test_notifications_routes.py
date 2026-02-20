import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, NotFoundError
from common.security import create_access_token
from app.domain.notification import Notification, NotificationType
from app.routes.notifications import router
from app.services.notification_service import NotificationService


@pytest.fixture
def mock_service():
    return AsyncMock(spec=NotificationService)


@pytest.fixture
def test_app(mock_service):
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    import app.main as main_module
    main_module.app_settings = type("S", (), {
        "jwt_secret": "test-secret",
        "jwt_algorithm": "HS256",
    })()
    main_module._notification_service = mock_service

    return app


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def user_token(user_id):
    return create_access_token(
        str(user_id), "test-secret",
        extra_claims={"role": "student", "is_verified": False},
    )


@pytest.fixture
def sample_notification(user_id):
    return Notification(
        id=uuid4(),
        user_id=user_id,
        type=NotificationType.ENROLLMENT,
        title="You enrolled in Python 101",
        body="Welcome!",
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_notification(client, mock_service, sample_notification, user_token):
    mock_service.create.return_value = sample_notification

    resp = await client.post("/notifications", json={
        "type": "enrollment",
        "title": "You enrolled in Python 101",
        "body": "Welcome!",
    }, headers={"Authorization": f"Bearer {user_token}"})

    assert resp.status_code == 201
    assert resp.json()["title"] == "You enrolled in Python 101"


@pytest.mark.asyncio
async def test_create_notification_no_auth(client):
    resp = await client.post("/notifications", json={
        "type": "enrollment",
        "title": "Test",
    })

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_my_notifications(client, mock_service, sample_notification, user_token):
    mock_service.list_my.return_value = ([sample_notification], 1)

    resp = await client.get("/notifications/me",
        headers={"Authorization": f"Bearer {user_token}"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


@pytest.mark.asyncio
async def test_mark_as_read(client, mock_service, sample_notification, user_token):
    read_notif = Notification(
        id=sample_notification.id,
        user_id=sample_notification.user_id,
        type=sample_notification.type,
        title=sample_notification.title,
        body=sample_notification.body,
        is_read=True,
        created_at=sample_notification.created_at,
    )
    mock_service.mark_as_read.return_value = read_notif

    resp = await client.patch(f"/notifications/{sample_notification.id}/read",
        headers={"Authorization": f"Bearer {user_token}"})

    assert resp.status_code == 200
    assert resp.json()["is_read"] is True


@pytest.mark.asyncio
async def test_mark_as_read_not_found(client, mock_service, user_token):
    mock_service.mark_as_read.side_effect = NotFoundError("Notification not found")

    resp = await client.patch(f"/notifications/{uuid4()}/read",
        headers={"Authorization": f"Bearer {user_token}"})

    assert resp.status_code == 404
