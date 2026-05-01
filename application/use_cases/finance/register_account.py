from application.dtos.finance import AccountRegisteredResponse, RegisterAccountCommand
from domain.entities.finance import Account
from domain.exceptions.finance import AccountAlreadyExistsError
from domain.repositories.finance import AccountRepository


class RegisterAccountUseCase:
    def __init__(self, account_repo: AccountRepository) -> None:
        self._account_repo = account_repo

    def execute(self, command: RegisterAccountCommand) -> AccountRegisteredResponse:
        if self._account_repo.exists_by_name_and_user(command.name, command.user_id):
            raise AccountAlreadyExistsError(command.name)

        account = Account(
            user_id=command.user_id,
            name=command.name,
            type=command.type,
            supported_currencies=command.supported_currencies,
            default_currencies=command.default_currencies,
        )
        self._account_repo.save(account)

        return AccountRegisteredResponse(
            account_id=account.id,
            name=account.name,
            type=account.type,
        )
