from application.dtos.user import ResetPasswordRequestCommand, ResetPasswordRequestResponse
from domain.entities.user import PasswordResetToken
from domain.repositories.user import PasswordResetTokenRepository, UserRepository


class ResetPasswordRequestUseCase:
    """
    Creates a password-reset token for the given email.

    If the email is not registered, the use case succeeds silently to avoid
    user enumeration. In production, the token would be delivered via email;
    it is returned in the response for development/testing purposes only.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: PasswordResetTokenRepository,
    ) -> None:
        self._user_repo = user_repo
        self._token_repo = token_repo

    def execute(self, command: ResetPasswordRequestCommand) -> ResetPasswordRequestResponse:
        user = self._user_repo.get_by_email(command.email)
        if user is None:
            return ResetPasswordRequestResponse(detail="If that email exists, a reset link was sent.")

        token = PasswordResetToken(user_id=user.id)
        self._token_repo.save(token)

        return ResetPasswordRequestResponse(
            detail="If that email exists, a reset link was sent.",
            reset_token=token.token,
        )
