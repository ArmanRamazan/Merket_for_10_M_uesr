from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class EnrollmentStatus(StrEnum):
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass(frozen=True)
class Enrollment:
    id: UUID
    student_id: UUID
    course_id: UUID
    payment_id: UUID | None
    status: EnrollmentStatus
    enrolled_at: datetime
    total_lessons: int = 0


class EnrollmentCreate(BaseModel):
    course_id: UUID
    payment_id: UUID | None = None
    total_lessons: int = 0


class EnrollmentResponse(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    payment_id: UUID | None
    status: EnrollmentStatus
    enrolled_at: datetime
    total_lessons: int = 0


class EnrollmentListResponse(BaseModel):
    items: list[EnrollmentResponse]
    total: int
