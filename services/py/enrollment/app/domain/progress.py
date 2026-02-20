from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


@dataclass(frozen=True)
class LessonProgress:
    id: UUID
    student_id: UUID
    lesson_id: UUID
    course_id: UUID
    completed_at: datetime


class LessonCompleteRequest(BaseModel):
    course_id: UUID


class CourseProgressResponse(BaseModel):
    course_id: UUID
    completed_lessons: int
    total_lessons: int
    percentage: float
