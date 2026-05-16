from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    is_admin: bool = True


class PasswordResetToken(BaseModel):
    model_config = ConfigDict(frozen=True)

    token: UUID = Field(default_factory=uuid4)
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used: bool = False
