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
