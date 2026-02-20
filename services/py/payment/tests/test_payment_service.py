import pytest
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from common.errors import ForbiddenError, NotFoundError
from app.domain.payment import Payment
from app.services.payment_service import PaymentService


@pytest.mark.asyncio
async def test_create_payment_success(
    payment_service: PaymentService,
    mock_repo: AsyncMock,
    sample_payment: Payment,
    student_id,
    course_id,
):
    mock_repo.create.return_value = sample_payment

    result = await payment_service.create(
        student_id=student_id,
        role="student",
        course_id=course_id,
        amount=Decimal("49.99"),
    )

    assert result.id == sample_payment.id
    assert result.status.value == "completed"
    mock_repo.create.assert_called_once_with(student_id, course_id, Decimal("49.99"))


@pytest.mark.asyncio
async def test_create_payment_teacher_forbidden(payment_service: PaymentService):
    with pytest.raises(ForbiddenError, match="Only students"):
        await payment_service.create(
            student_id=uuid4(),
            role="teacher",
            course_id=uuid4(),
            amount=Decimal("49.99"),
        )


@pytest.mark.asyncio
async def test_get_payment_success(
    payment_service: PaymentService,
    mock_repo: AsyncMock,
    sample_payment: Payment,
):
    mock_repo.get_by_id.return_value = sample_payment

    result = await payment_service.get(sample_payment.id)

    assert result.id == sample_payment.id
    mock_repo.get_by_id.assert_called_once_with(sample_payment.id)


@pytest.mark.asyncio
async def test_get_payment_not_found(
    payment_service: PaymentService,
    mock_repo: AsyncMock,
):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError, match="Payment not found"):
        await payment_service.get(uuid4())


@pytest.mark.asyncio
async def test_list_my_payments(
    payment_service: PaymentService,
    mock_repo: AsyncMock,
    sample_payment: Payment,
    student_id,
):
    mock_repo.list_by_student.return_value = ([sample_payment], 1)

    items, total = await payment_service.list_my(student_id, limit=20, offset=0)

    assert len(items) == 1
    assert total == 1
    mock_repo.list_by_student.assert_called_once_with(student_id, 20, 0)
