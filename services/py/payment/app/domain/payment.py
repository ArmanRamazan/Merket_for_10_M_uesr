from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass(frozen=True)
class Payment:
    id: UUID
    student_id: UUID
    course_id: UUID
    amount: Decimal
    status: PaymentStatus
    created_at: datetime


class PaymentCreate(BaseModel):
    course_id: UUID
    amount: Decimal = Field(gt=0)


class PaymentResponse(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    amount: Decimal
    status: PaymentStatus
    created_at: datetime


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
