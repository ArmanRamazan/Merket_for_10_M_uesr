from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


@dataclass(frozen=True)
class RefreshToken:
    id: UUID
    user_id: UUID
    token_hash: str
    family_id: UUID
    is_revoked: bool
    expires_at: datetime
    created_at: datetime


class RefreshRequest(BaseModel):
    refresh_token: str
