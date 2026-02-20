from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


@dataclass(frozen=True)
class Module:
    id: UUID
    course_id: UUID
    title: str
    order: int
    created_at: datetime


class ModuleCreate(BaseModel):
    title: str
    order: int = 0


class ModuleUpdate(BaseModel):
    title: str | None = None
    order: int | None = None


class ModuleResponse(BaseModel):
    id: UUID
    course_id: UUID
    title: str
    order: int
    created_at: datetime
