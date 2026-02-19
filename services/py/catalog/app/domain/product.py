from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


@dataclass(frozen=True)
class Product:
    id: UUID
    seller_id: UUID
    title: str
    description: str
    price: Decimal
    stock: int
    created_at: datetime


class ProductCreate(BaseModel):
    title: str
    description: str
    price: Decimal
    stock: int


class ProductResponse(BaseModel):
    id: UUID
    seller_id: UUID
    title: str
    description: str
    price: Decimal
    stock: int
    created_at: datetime


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
