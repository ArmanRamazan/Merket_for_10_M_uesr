from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from common.errors import ForbiddenError, NotFoundError
from app.domain.payment import Payment
from app.repositories.payment_repo import PaymentRepository


class PaymentService:
    def __init__(self, repo: PaymentRepository) -> None:
        self._repo = repo

    async def create(
        self,
        student_id: UUID,
        role: str,
        course_id: UUID,
        amount: Decimal,
    ) -> Payment:
        if role != "student":
            raise ForbiddenError("Only students can make payments")
        return await self._repo.create(student_id, course_id, amount)

    async def get(self, payment_id: UUID) -> Payment:
        payment = await self._repo.get_by_id(payment_id)
        if not payment:
            raise NotFoundError("Payment not found")
        return payment

    async def list_my(
        self, student_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[Payment], int]:
        return await self._repo.list_by_student(student_id, limit, offset)
