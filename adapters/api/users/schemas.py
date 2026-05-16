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


class UpdateProfileRequest(Schema):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class ChangePasswordRequest(Schema):
    current_password: str
    new_password: str


class ResetPasswordRequestSchema(Schema):
    email: str


class ResetPasswordRequestResponseSchema(Schema):
    detail: str
    reset_token: UUID | None = None


class ResetPasswordConfirmSchema(Schema):
    token: UUID
    new_password: str
