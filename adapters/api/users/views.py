from http import HTTPStatus
from uuid import UUID

from ninja import Router

from adapters.api.users.schemas import (
    ChangePasswordRequest,
    ErrorResponse,
    LoginRequest,
    RegisterRequest,
    ResetPasswordConfirmSchema,
    ResetPasswordRequestResponseSchema,
    ResetPasswordRequestSchema,
    UpdateProfileRequest,
    UserResponse,
)
from application.dtos.user import (
    AuthenticateUserCommand,
    ChangePasswordCommand,
    GetUserProfileQuery,
    RegisterUserCommand,
    ResetPasswordConfirmCommand,
    ResetPasswordRequestCommand,
    UpdateProfileCommand,
)
from domain.exceptions.user import (
    AdminRequiredError,
    EmailAlreadyTakenError,
    InvalidCredentialsError,
    InvalidCurrentPasswordError,
    InvalidResetTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from infrastructure.di import (
    get_authenticate_user_use_case,
    get_change_password_use_case,
    get_register_user_use_case,
    get_reset_password_confirm_use_case,
    get_reset_password_request_use_case,
    get_update_profile_use_case,
    get_user_profile_use_case,
)

router = Router(tags=["auth"])


def _require_auth(request) -> tuple[str | None, UUID | None]:
    """Return (error_msg, user_id) — exactly one will be None."""
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return "Not authenticated.", None
    try:
        return None, UUID(user_id_str)
    except ValueError:
        return "Invalid session.", None


def _require_admin(request) -> tuple[str | None, UUID | None]:
    """Like _require_auth, but also verifies is_admin=True on the user record."""
    err, user_id = _require_auth(request)
    if err:
        return err, None
    uc = get_user_profile_use_case()
    try:
        profile = uc.execute(GetUserProfileQuery(user_id=user_id))
    except UserNotFoundError:
        return "Session user no longer exists.", None
    if not profile.is_admin:
        return "Administrator privileges required.", None
    return None, user_id


@router.post(
    "/register",
    response={HTTPStatus.CREATED: UserResponse, HTTPStatus.CONFLICT: ErrorResponse, HTTPStatus.FORBIDDEN: ErrorResponse},
    summary="Register a new user (admin only once users exist)",
)
def register(request, payload: RegisterRequest):
    """
    U2: Only administrators can create new user accounts.
    The very first registration is always allowed (bootstrapping).
    """
    from infrastructure.django_app.models.user import UserModel
    user_count = UserModel.objects.count()
    if user_count > 0:
        # Subsequent registrations require an existing admin session
        err, _ = _require_admin(request)
        if err:
            return HTTPStatus.FORBIDDEN, ErrorResponse(detail="Only admins can register new users.")

    uc = get_register_user_use_case()
    try:
        result = uc.execute(
            RegisterUserCommand(
                first_name=payload.first_name,
                last_name=payload.last_name,
                email=payload.email,
                password=payload.password,
            )
        )
        if user_count == 0:
            # Auto-login on first-ever registration
            request.session["user_id"] = str(result.user_id)
            request.session["full_name"] = result.full_name
        return HTTPStatus.CREATED, UserResponse(
            user_id=result.user_id,
            email=result.email,
            full_name=result.full_name,
            is_admin=result.is_admin,
        )
    except UserAlreadyExistsError as exc:
        return HTTPStatus.CONFLICT, ErrorResponse(detail=str(exc))


@router.post(
    "/login",
    response={HTTPStatus.OK: UserResponse, HTTPStatus.UNAUTHORIZED: ErrorResponse},
    summary="Authenticate a user",
)
def login(request, payload: LoginRequest):
    uc = get_authenticate_user_use_case()
    try:
        result = uc.execute(
            AuthenticateUserCommand(
                email=payload.email,
                password=payload.password,
            )
        )
        request.session["user_id"] = str(result.user_id)
        request.session["full_name"] = result.full_name
        return HTTPStatus.OK, UserResponse(
            user_id=result.user_id,
            email=result.email,
            full_name=result.full_name,
            is_admin=result.is_admin,
        )
    except InvalidCredentialsError as exc:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail=str(exc))


@router.get(
    "/me",
    response={HTTPStatus.OK: UserResponse, HTTPStatus.UNAUTHORIZED: ErrorResponse},
    summary="Get authenticated user profile",
)
def me(request):
    err, user_id = _require_auth(request)
    if err:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail=err)

    uc = get_user_profile_use_case()
    try:
        result = uc.execute(GetUserProfileQuery(user_id=user_id))
        return HTTPStatus.OK, UserResponse(
            user_id=result.user_id,
            email=result.email,
            full_name=result.full_name,
            is_admin=result.is_admin,
        )
    except UserNotFoundError:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Session user no longer exists.")


@router.patch(
    "/me",
    response={
        HTTPStatus.OK: UserResponse,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
        HTTPStatus.CONFLICT: ErrorResponse,
    },
    summary="Update profile (first name, last name, email)",
)
def update_profile(request, payload: UpdateProfileRequest):
    """U4 — Update the authenticated user's profile."""
    err, user_id = _require_auth(request)
    if err:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail=err)

    uc = get_update_profile_use_case()
    try:
        result = uc.execute(
            UpdateProfileCommand(
                user_id=user_id,
                first_name=payload.first_name,
                last_name=payload.last_name,
                email=payload.email,
            )
        )
        # Refresh session full_name if it changed
        if payload.first_name or payload.last_name:
            request.session["full_name"] = result.full_name
        return HTTPStatus.OK, UserResponse(
            user_id=result.user_id,
            email=result.email,
            full_name=result.full_name,
            is_admin=result.is_admin,
        )
    except UserNotFoundError:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Session user no longer exists.")
    except EmailAlreadyTakenError as exc:
        return HTTPStatus.CONFLICT, ErrorResponse(detail=str(exc))


@router.post(
    "/me/change-password",
    response={
        HTTPStatus.OK: dict,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
    summary="Change password (requires current password)",
)
def change_password(request, payload: ChangePasswordRequest):
    """U5 — Change password for the authenticated user."""
    err, user_id = _require_auth(request)
    if err:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail=err)

    uc = get_change_password_use_case()
    try:
        uc.execute(
            ChangePasswordCommand(
                user_id=user_id,
                current_password=payload.current_password,
                new_password=payload.new_password,
            )
        )
        return HTTPStatus.OK, {"detail": "Password changed successfully."}
    except UserNotFoundError:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Session user no longer exists.")
    except InvalidCurrentPasswordError as exc:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail=str(exc))


@router.post(
    "/password-reset/request",
    response={HTTPStatus.OK: ResetPasswordRequestResponseSchema},
    summary="Request a password reset token (sent via email in production)",
)
def password_reset_request(request, payload: ResetPasswordRequestSchema):
    """U3 — Initiate password reset. Token is returned in response (dev mode)."""
    uc = get_reset_password_request_use_case()
    result = uc.execute(ResetPasswordRequestCommand(email=payload.email))
    return HTTPStatus.OK, {"detail": result.detail, "reset_token": result.reset_token}


@router.post(
    "/password-reset/confirm",
    response={
        HTTPStatus.OK: dict,
        HTTPStatus.UNPROCESSABLE_ENTITY: ErrorResponse,
    },
    summary="Confirm password reset using the token",
)
def password_reset_confirm(request, payload: ResetPasswordConfirmSchema):
    """U3 — Set a new password using a valid reset token."""
    uc = get_reset_password_confirm_use_case()
    try:
        uc.execute(
            ResetPasswordConfirmCommand(
                token=payload.token,
                new_password=payload.new_password,
            )
        )
        return HTTPStatus.OK, {"detail": "Password reset successfully."}
    except InvalidResetTokenError as exc:
        return HTTPStatus.UNPROCESSABLE_ENTITY, ErrorResponse(detail=str(exc))
    except UserNotFoundError as exc:
        return HTTPStatus.UNPROCESSABLE_ENTITY, ErrorResponse(detail=str(exc))


@router.post(
    "/logout",
    response={HTTPStatus.OK: dict},
    summary="End the current session",
)
def logout(request):
    request.session.flush()
    return HTTPStatus.OK, {"detail": "Logged out successfully."}
