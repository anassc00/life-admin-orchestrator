from contextlib import contextmanager, nullcontext
from decimal import Decimal
from typing import Callable, Iterator

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
        atomic_context: Callable[[], "Iterator[None]"] | None = None,
    ) -> None:
        self._goal_repo = savings_goal_repo
        self._deposit_repo = savings_deposit_repo
        self._tx_repo = transaction_repo
        self._account_repo = account_repo
        # Allow injection of an atomic context (e.g. django.db.transaction.atomic).
        # Falls back to nullcontext so tests and non-Django callers work without changes.
        self._atomic = atomic_context if atomic_context is not None else nullcontext

    def execute(self, command: DepositToSavingsCommand) -> SavingsDepositCreatedResponse:
        # Verify the goal exists
        goal = self._goal_repo.get_by_id(command.goal_id)
        if goal is None:
            raise SavingsGoalNotFoundError(command.goal_id)

        # Enforce USD/USDT constraint
        if command.currency not in _ALLOWED_CURRENCIES:
            raise SavingsDepositCurrencyError()

        deposit = SavingsDeposit(
            user_id=command.user_id,
            goal_id=command.goal_id,
            account_id=command.account_id,
            amount=command.amount,
            currency=command.currency,
            date=command.date,
            notes=command.notes,
        )
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

        # Both writes happen atomically — if either fails, neither is committed.
        with self._atomic():
            self._deposit_repo.save(deposit)
            self._tx_repo.save(tx)

            # Auto-complete the goal when total USD deposits reach the target
            if not goal.is_completed and command.currency == Currency.USD:
                all_deposits = self._deposit_repo.list_by_goal(goal.id)
                total_usd = sum(
                    (d.amount for d in all_deposits if d.currency == Currency.USD), Decimal("0")
                )
                if total_usd >= goal.target_amount_usd:
                    completed_goal = goal.model_copy(update={"is_completed": True})
                    self._goal_repo.save(completed_goal)

        return SavingsDepositCreatedResponse(
            deposit_id=deposit.id,
            goal_id=deposit.goal_id,
            amount=deposit.amount,
            currency=deposit.currency,
        )
