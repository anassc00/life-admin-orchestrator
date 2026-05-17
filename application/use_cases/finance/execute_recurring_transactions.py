"""F10 — Generate actual transactions from active recurring definitions that are due."""

import uuid
from datetime import date
from decimal import Decimal

from domain.entities.finance import RecurringTransaction, Transaction, TransactionType
from domain.repositories.finance import (
    AccountRepository,
    RecurringTransactionRepository,
    TransactionRepository,
)


class ExecuteRecurringTransactionsUseCase:
    def __init__(
        self,
        rt_repo: RecurringTransactionRepository,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
    ) -> None:
        self._rt_repo = rt_repo
        self._tx_repo = transaction_repo
        self._account_repo = account_repo

    def execute(self, as_of_date: date) -> int:
        """Generate transactions for all due recurring definitions.

        Returns the number of transactions created.
        """
        due = self._rt_repo.list_active_due(as_of_date)
        created = 0
        for rt in due:
            try:
                self._generate(rt, as_of_date)
                updated = rt.model_copy(update={"last_generated": as_of_date})
                self._rt_repo.save(updated)
                created += 1
            except Exception:
                # Skip failed entries; they will be retried next run
                pass
        return created

    def _generate(self, rt: RecurringTransaction, on_date: date) -> None:
        account = self._account_repo.get_by_id(rt.account_id)
        if account is None:
            return
        # Use exchange_rate = 1 for same-currency transactions; USD amounts are native
        tx = Transaction(
            id=uuid.uuid4(),
            user_id=rt.user_id,
            account_id=rt.account_id,
            type=rt.type,
            amount=rt.amount,
            currency=rt.currency,
            exchange_rate=Decimal("1"),
            category_id=rt.category_id,
            description=f"[Auto] {rt.description}",
            date=on_date,
        )
        self._tx_repo.save(tx)
