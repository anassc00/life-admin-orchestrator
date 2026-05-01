from application.dtos.user import AuthenticatedUserResponse, AuthenticateUserCommand
from domain.exceptions.user import InvalidCredentialsError
from domain.repositories.user import PasswordHasher, UserRepository


class AuthenticateUserUseCase:
    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher) -> None:
        self._repo = user_repo
        self._hasher = password_hasher

    def execute(self, command: AuthenticateUserCommand) -> AuthenticatedUserResponse:
        user = self._repo.get_by_email(command.email)
        if user is None:
            raise InvalidCredentialsError()

        if not self._hasher.verify(command.password, user.hashed_password):
            raise InvalidCredentialsError()

        return AuthenticatedUserResponse(
            user_id=user.id,
            email=user.email,
            full_name=f"{user.first_name} {user.last_name}",
            is_admin=user.is_admin,
        )
