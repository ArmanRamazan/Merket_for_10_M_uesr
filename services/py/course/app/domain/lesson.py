from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


@dataclass(frozen=True)
class Lesson:
    id: UUID
    module_id: UUID
    title: str
    content: str
    video_url: str | None
    duration_minutes: int
    order: int
    created_at: datetime


class LessonCreate(BaseModel):
    title: str
    content: str = ""
    video_url: str | None = None
    duration_minutes: int = 0
    order: int = 0


class LessonUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    video_url: str | None = None
    duration_minutes: int | None = None
    order: int | None = None


class LessonResponse(BaseModel):
    id: UUID
    module_id: UUID
    title: str
    content: str
    video_url: str | None
    duration_minutes: int
    order: int
    created_at: datetime
