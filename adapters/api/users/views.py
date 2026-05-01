from http import HTTPStatus

from ninja import Router

from adapters.api.users.schemas import ErrorResponse, LoginRequest, RegisterRequest, UserResponse
from application.dtos.user import AuthenticateUserCommand, RegisterUserCommand
from domain.exceptions.user import InvalidCredentialsError, UserAlreadyExistsError
from infrastructure.di import get_authenticate_user_use_case, get_register_user_use_case

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
        return HTTPStatus.OK, UserResponse(
            user_id=result.user_id,
            email=result.email,
            full_name=result.full_name,
            is_admin=result.is_admin,
        )
    except InvalidCredentialsError as exc:
        return HTTPStatus.UNAUTHORIZED, ErrorResponse(detail=str(exc))
