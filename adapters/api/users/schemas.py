from uuid import UUID

from ninja import Schema


class RegisterRequest(Schema):
    first_name: str
    last_name: str
    email: str
    password: str


class LoginRequest(Schema):
    email: str
    password: str


class UserResponse(Schema):
    user_id: UUID
    email: str
    full_name: str
    is_admin: bool


class ErrorResponse(Schema):
    detail: str
