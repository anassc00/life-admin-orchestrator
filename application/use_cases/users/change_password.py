from application.dtos.user import ChangePasswordCommand
from domain.exceptions.user import InvalidCurrentPasswordError, UserNotFoundError
from domain.repositories.user import PasswordHasher, UserRepository


class ChangePasswordUseCase:
    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    def execute(self, command: ChangePasswordCommand) -> None:
        user = self._user_repo.get_by_id(command.user_id)
        if user is None:
            raise UserNotFoundError(command.user_id)

        if not self._password_hasher.verify(command.current_password, user.hashed_password):
            raise InvalidCurrentPasswordError()

        new_hash = self._password_hasher.hash(command.new_password)
        self._user_repo.save(user.model_copy(update={"hashed_password": new_hash}))
