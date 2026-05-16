from uuid import UUID

from pydantic import BaseModel


# --- Update Profile ---


class UpdateProfileCommand(BaseModel):
    user_id: UUID
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class UpdateProfileResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    is_admin: bool


# --- Change Password ---


class ChangePasswordCommand(BaseModel):
    user_id: UUID
    current_password: str
    new_password: str


# --- Password Reset ---


class ResetPasswordRequestCommand(BaseModel):
    email: str


class ResetPasswordRequestResponse(BaseModel):
    detail: str
    reset_token: UUID | None = None  # returned for dev; in prod would be emailed


class ResetPasswordConfirmCommand(BaseModel):
    token: UUID
    new_password: str


# --- Register / Auth ---


class RegisterUserCommand(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class AuthenticateUserCommand(BaseModel):
    email: str
    password: str


class GetUserProfileQuery(BaseModel):
    user_id: UUID


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


class UserProfileResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    is_admin: bool
