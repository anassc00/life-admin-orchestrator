from datetime import datetime, timedelta, timezone

from application.dtos.user import ResetPasswordConfirmCommand
from domain.exceptions.user import InvalidResetTokenError, UserNotFoundError
from domain.repositories.user import PasswordHasher, PasswordResetTokenRepository, UserRepository

TOKEN_TTL_HOURS = 1


class ResetPasswordConfirmUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: PasswordResetTokenRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repo = user_repo
        self._token_repo = token_repo
        self._password_hasher = password_hasher

    def execute(self, command: ResetPasswordConfirmCommand) -> None:
        token = self._token_repo.get_by_token(command.token)
        if token is None or token.used:
            raise InvalidResetTokenError()

        # Tokens expire after TOKEN_TTL_HOURS
        expiry = token.created_at.replace(tzinfo=timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS)
        if datetime.now(tz=timezone.utc) > expiry:
            raise InvalidResetTokenError()

        user = self._user_repo.get_by_id(token.user_id)
        if user is None:
            raise UserNotFoundError(token.user_id)

        new_hash = self._password_hasher.hash(command.new_password)
        self._user_repo.save(user.model_copy(update={"hashed_password": new_hash}))
        self._token_repo.mark_used(command.token)
