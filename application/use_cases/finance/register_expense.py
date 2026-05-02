from application.dtos.finance import ExpenseRegisteredResponse, RegisterExpenseCommand
from domain.entities.finance import Transaction, TransactionType
from domain.exceptions.finance import (
    AccountAccessForbiddenError,
    AccountNotFoundError,
    ExpenseCategoryNotFoundError,
)
from domain.repositories.finance import (
    AccountRepository,
    ExpenseCategoryRepository,
    TransactionRepository,
)


class RegisterExpenseUseCase:
    def __init__(
        self,
        account_repo: AccountRepository,
        category_repo: ExpenseCategoryRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._account_repo = account_repo
        self._category_repo = category_repo
        self._transaction_repo = transaction_repo

    def execute(self, command: RegisterExpenseCommand) -> ExpenseRegisteredResponse:
        account = self._account_repo.get_by_id(command.account_id)
        if account is None:
            raise AccountNotFoundError(command.account_id)

        if account.user_id != command.user_id:
            raise AccountAccessForbiddenError()

        category = self._category_repo.get_by_id(command.category_id)
        if category is None:
            raise ExpenseCategoryNotFoundError(command.category_id)

        tx = Transaction(
            user_id=command.user_id,
            account_id=command.account_id,
            type=TransactionType.EXPENSE,
            amount=command.amount,
            currency=command.currency,
            exchange_rate=command.exchange_rate,
            category_id=command.category_id,
            description=command.description,
            date=command.date,
        )
        self._transaction_repo.save(tx)

        return ExpenseRegisteredResponse(
            transaction_id=tx.id,
            amount=tx.amount,
            currency=tx.currency,
            category_id=tx.category_id,  # type: ignore[arg-type]
            description=tx.description,
        )
