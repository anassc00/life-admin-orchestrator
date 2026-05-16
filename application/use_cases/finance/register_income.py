from application.dtos.finance import IncomeRegisteredResponse, RegisterIncomeCommand
from domain.entities.finance import Transaction, TransactionType
from domain.exceptions.finance import (
    AccountAccessForbiddenError,
    AccountNotFoundError,
    DuplicateBaseSalaryError,
)
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

        # F4: enforce at most one base-salary per calendar month
        if command.is_base_salary:
            existing = self._transaction_repo.get_base_salary_by_period(
                command.user_id, command.date.year, command.date.month
            )
            if existing is not None:
                raise DuplicateBaseSalaryError(command.date.year, command.date.month)

        tx = Transaction(
            user_id=command.user_id,
            account_id=command.account_id,
            type=TransactionType.INCOME,
            amount=command.amount,
            currency=command.currency,
            exchange_rate=command.exchange_rate,
            category=command.category,
            is_base_salary=command.is_base_salary,
            date=command.date,
            notes=command.notes,
        )
        self._transaction_repo.save(tx)

        return IncomeRegisteredResponse(
            transaction_id=tx.id,
            type=tx.type,
            amount=tx.amount,
            currency=tx.currency,
            is_base_salary=tx.is_base_salary,
            notes=tx.notes,
        )
