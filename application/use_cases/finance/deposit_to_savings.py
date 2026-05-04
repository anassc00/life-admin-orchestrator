from decimal import Decimal

from application.dtos.finance import DepositToSavingsCommand, SavingsDepositCreatedResponse
from domain.entities.finance import Currency, SavingsDeposit, Transaction, TransactionType
from domain.exceptions.finance import SavingsDepositCurrencyError, SavingsGoalNotFoundError
from domain.repositories.finance import (
    AccountRepository,
    SavingsDepositRepository,
    SavingsGoalRepository,
    TransactionRepository,
)

_ALLOWED_CURRENCIES = {Currency.USD, Currency.USDT}


class DepositToSavingsUseCase:
    def __init__(
        self,
        savings_goal_repo: SavingsGoalRepository,
        savings_deposit_repo: SavingsDepositRepository,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
    ) -> None:
        self._goal_repo = savings_goal_repo
        self._deposit_repo = savings_deposit_repo
        self._tx_repo = transaction_repo
        self._account_repo = account_repo

    def execute(self, command: DepositToSavingsCommand) -> SavingsDepositCreatedResponse:
        # Verify the goal exists
        goal = self._goal_repo.get_by_id(command.goal_id)
        if goal is None:
            raise SavingsGoalNotFoundError(command.goal_id)

        # Enforce USD/USDT constraint
        if command.currency not in _ALLOWED_CURRENCIES:
            raise SavingsDepositCurrencyError()

        # Record the deposit
        deposit = SavingsDeposit(
            user_id=command.user_id,
            goal_id=command.goal_id,
            account_id=command.account_id,
            amount=command.amount,
            currency=command.currency,
            date=command.date,
            notes=command.notes,
        )
        self._deposit_repo.save(deposit)

        # Create a SAVINGS transaction so the balance is updated
        tx = Transaction(
            user_id=command.user_id,
            account_id=command.account_id,
            type=TransactionType.SAVINGS,
            amount=command.amount,
            currency=command.currency,
            exchange_rate=Decimal("1"),  # USD/USDT → rate is always 1
            date=command.date,
            notes=f"Savings deposit: {goal.motive}",
        )
        self._tx_repo.save(tx)

        return SavingsDepositCreatedResponse(
            deposit_id=deposit.id,
            goal_id=deposit.goal_id,
            amount=deposit.amount,
            currency=deposit.currency,
        )
