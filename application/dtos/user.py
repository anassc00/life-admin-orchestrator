from uuid import UUID

from pydantic import BaseModel


class RegisterUserCommand(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class AuthenticateUserCommand(BaseModel):
    email: str
    password: str


class UserRegisteredResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    is_admin: bool


class AuthenticatedUserResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    is_admin: bool
