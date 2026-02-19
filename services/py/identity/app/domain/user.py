from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


@dataclass(frozen=True)
class User:
    id: UUID
    email: str
    password_hash: str
    name: str
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: datetime
