from application.dtos.user import UpdateProfileCommand, UpdateProfileResponse
from domain.exceptions.user import EmailAlreadyTakenError, UserNotFoundError
from domain.repositories.user import UserRepository


class UpdateProfileUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    def execute(self, command: UpdateProfileCommand) -> UpdateProfileResponse:
        user = self._user_repo.get_by_id(command.user_id)
        if user is None:
            raise UserNotFoundError(command.user_id)

        if command.email is not None and command.email != user.email:
            if self._user_repo.email_taken_by_other(command.email, command.user_id):
                raise EmailAlreadyTakenError(command.email)

        update_fields: dict = {}
        if command.first_name is not None:
            update_fields["first_name"] = command.first_name
        if command.last_name is not None:
            update_fields["last_name"] = command.last_name
        if command.email is not None:
            update_fields["email"] = command.email

        updated = user.model_copy(update=update_fields)
        self._user_repo.save(updated)

        return UpdateProfileResponse(
            user_id=updated.id,
            email=updated.email,
            full_name=f"{updated.first_name} {updated.last_name}",
            is_admin=updated.is_admin,
        )
