from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class Review:
    id: UUID
    student_id: UUID
    course_id: UUID
    rating: int
    comment: str
    created_at: datetime


class ReviewCreate(BaseModel):
    course_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str = ""


class ReviewResponse(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    rating: int
    comment: str
    created_at: datetime


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
