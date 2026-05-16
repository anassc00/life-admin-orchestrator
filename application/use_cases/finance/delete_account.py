from application.dtos.finance import AccountDeletedResponse, DeleteAccountCommand
from domain.exceptions.finance import (
    AccountAccessForbiddenError,
    AccountHasTransactionsError,
    AccountNotFoundError,
)
from domain.repositories.finance import AccountRepository, TransactionRepository


class DeleteAccountUseCase:
    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._account_repo = account_repo
        self._transaction_repo = transaction_repo

    def execute(self, command: DeleteAccountCommand) -> AccountDeletedResponse:
        account = self._account_repo.get_by_id(command.account_id)
        if account is None:
            raise AccountNotFoundError(command.account_id)

        if account.user_id != command.user_id:
            raise AccountAccessForbiddenError()

        if self._transaction_repo.has_transactions_for_account(command.account_id):
            raise AccountHasTransactionsError()

        self._account_repo.delete(command.account_id)
        return AccountDeletedResponse(account_id=command.account_id)
