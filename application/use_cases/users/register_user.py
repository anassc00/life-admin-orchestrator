from application.dtos.user import RegisterUserCommand, UserRegisteredResponse
from domain.entities.user import User
from domain.exceptions.user import UserAlreadyExistsError
from domain.repositories.user import PasswordHasher, UserRepository


class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher) -> None:
        self._repo = user_repo
        self._hasher = password_hasher

    def execute(self, command: RegisterUserCommand) -> UserRegisteredResponse:
        existing = self._repo.get_by_email(command.email)
        if existing is not None:
            raise UserAlreadyExistsError(command.email)

        hashed = self._hasher.hash(command.password)
        user = User(
            first_name=command.first_name,
            last_name=command.last_name,
            email=command.email,
            hashed_password=hashed,
        )
        self._repo.save(user)

        return UserRegisteredResponse(
            user_id=user.id,
            email=user.email,
            full_name=f"{user.first_name} {user.last_name}",
            is_admin=user.is_admin,
        )
