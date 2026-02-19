from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class CourseLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass(frozen=True)
class Course:
    id: UUID
    teacher_id: UUID
    title: str
    description: str
    is_free: bool
    price: Decimal | None
    duration_minutes: int
    level: CourseLevel
    created_at: datetime


class CourseCreate(BaseModel):
    title: str
    description: str = ""
    is_free: bool = True
    price: Decimal | None = None
    duration_minutes: int = 0
    level: CourseLevel = CourseLevel.BEGINNER


class CourseResponse(BaseModel):
    id: UUID
    teacher_id: UUID
    title: str
    description: str
    is_free: bool
    price: Decimal | None
    duration_minutes: int
    level: CourseLevel
    created_at: datetime


class CourseListResponse(BaseModel):
    items: list[CourseResponse]
    total: int
