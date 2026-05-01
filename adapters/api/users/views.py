from http import HTTPStatus
from uuid import UUID

from ninja import Router

from adapters.api.users.schemas import ErrorResponse, LoginRequest, RegisterRequest, UserResponse
from application.dtos.user import AuthenticateUserCommand, GetUserProfileQuery, RegisterUserCommand
from domain.exceptions.user import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from infrastructure.di import (
    get_authenticate_user_use_case,
    get_register_user_use_case,
    get_user_profile_use_case,
)

router = Router(tags=["auth"])


@router.post(
    "/register",
    response={HTTPStatus.CREATED: UserResponse, HTTPStatus.CONFLICT: ErrorResponse},
    summary="Register a new admin user",
)
def register(request, payload: RegisterRequest):
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
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Not authenticated.")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail="Invalid session.")

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


@router.post(
    "/logout",
    response={HTTPStatus.OK: dict},
    summary="End the current session",
)
def logout(request):
    request.session.flush()
    return HTTPStatus.OK, {"detail": "Logged out successfully."}
