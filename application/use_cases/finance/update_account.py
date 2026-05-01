from application.dtos.finance import AccountUpdatedResponse, UpdateAccountCommand
from domain.exceptions.finance import AccountAccessForbiddenError, AccountNotFoundError
from domain.repositories.finance import AccountRepository


class UpdateAccountUseCase:
    def __init__(self, account_repo: AccountRepository) -> None:
        self._account_repo = account_repo

    def execute(self, command: UpdateAccountCommand) -> AccountUpdatedResponse:
        account = self._account_repo.get_by_id(command.account_id)
        if account is None:
            raise AccountNotFoundError(command.account_id)

        if account.user_id != command.user_id:
            raise AccountAccessForbiddenError()

        updated = account.model_copy(
            update={
                "name": command.name,
                "type": command.type,
                "supported_currencies": command.supported_currencies,
                "default_currencies": command.default_currencies,
            }
        )
        self._account_repo.save(updated)

        return AccountUpdatedResponse(
            account_id=updated.id,
            name=updated.name,
            type=updated.type,
            supported_currencies=updated.supported_currencies,
            default_currencies=updated.default_currencies,
        )
