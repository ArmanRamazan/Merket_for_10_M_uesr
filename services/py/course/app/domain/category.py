from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel


@dataclass(frozen=True)
class Category:
    id: UUID
    name: str
    slug: str


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
