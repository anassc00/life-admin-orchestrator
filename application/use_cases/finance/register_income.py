from application.dtos.finance import IncomeRegisteredResponse, RegisterIncomeCommand
from domain.entities.finance import Transaction, TransactionType
from domain.exceptions.finance import AccountAccessForbiddenError, AccountNotFoundError
from domain.repositories.finance import AccountRepository, TransactionRepository


class RegisterIncomeUseCase:
    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._account_repo = account_repo
        self._transaction_repo = transaction_repo

    def execute(self, command: RegisterIncomeCommand) -> IncomeRegisteredResponse:
        account = self._account_repo.get_by_id(command.account_id)
        if account is None:
            raise AccountNotFoundError(command.account_id)

        if account.user_id != command.user_id:
            raise AccountAccessForbiddenError()

        tx = Transaction(
            user_id=command.user_id,
            account_id=command.account_id,
            type=TransactionType.INCOME,
            amount=command.amount,
            currency=command.currency,
            exchange_rate=command.exchange_rate,
            category=command.category,
            date=command.date,
            notes=command.notes,
        )
        self._transaction_repo.save(tx)

        return IncomeRegisteredResponse(
            transaction_id=tx.id,
            type=tx.type,
            amount=tx.amount,
            currency=tx.currency,
            notes=tx.notes,
        )
