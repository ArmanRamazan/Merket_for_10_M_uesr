import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, ForbiddenError, NotFoundError
from common.security import create_access_token
from app.domain.payment import Payment, PaymentStatus
from app.routes.payments import router
from app.services.payment_service import PaymentService


@pytest.fixture
def mock_service():
    return AsyncMock(spec=PaymentService)


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
    main_module._payment_service = mock_service

    return app


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def student_id():
    return uuid4()


@pytest.fixture
def student_token(student_id):
    return create_access_token(
        str(student_id), "test-secret",
        extra_claims={"role": "student", "is_verified": False},
    )


@pytest.fixture
def teacher_token():
    return create_access_token(
        str(uuid4()), "test-secret",
        extra_claims={"role": "teacher", "is_verified": True},
    )


@pytest.fixture
def course_id():
    return uuid4()


@pytest.fixture
def sample_payment(student_id, course_id):
    return Payment(
        id=uuid4(),
        student_id=student_id,
        course_id=course_id,
        amount=Decimal("49.99"),
        status=PaymentStatus.COMPLETED,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_payment_success(client, mock_service, sample_payment, student_token, course_id):
    mock_service.create.return_value = sample_payment

    resp = await client.post("/payments", json={
        "course_id": str(course_id),
        "amount": "49.99",
    }, headers={"Authorization": f"Bearer {student_token}"})

    assert resp.status_code == 201
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_create_payment_teacher_forbidden(client, mock_service, teacher_token, course_id):
    mock_service.create.side_effect = ForbiddenError("Only students can make payments")

    resp = await client.post("/payments", json={
        "course_id": str(course_id),
        "amount": "49.99",
    }, headers={"Authorization": f"Bearer {teacher_token}"})

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_payment_no_auth(client):
    resp = await client.post("/payments", json={
        "course_id": str(uuid4()),
        "amount": "49.99",
    })

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_payment_success(client, mock_service, sample_payment, student_token):
    mock_service.get.return_value = sample_payment

    resp = await client.get(f"/payments/{sample_payment.id}",
        headers={"Authorization": f"Bearer {student_token}"})

    assert resp.status_code == 200
    assert resp.json()["id"] == str(sample_payment.id)


@pytest.mark.asyncio
async def test_get_payment_not_found(client, mock_service, student_token):
    mock_service.get.side_effect = NotFoundError("Payment not found")

    resp = await client.get(f"/payments/{uuid4()}",
        headers={"Authorization": f"Bearer {student_token}"})

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_my_payments(client, mock_service, sample_payment, student_token):
    mock_service.list_my.return_value = ([sample_payment], 1)

    resp = await client.get("/payments/me",
        headers={"Authorization": f"Bearer {student_token}"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
