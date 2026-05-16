"""In-memory repository implementations for unit testing.

These satisfy the domain repository interfaces without touching
the database, so use cases can be tested in complete isolation.
"""

from datetime import date
from uuid import UUID

from domain.entities.finance import Expense, Invoice
from domain.repositories.finance import ExpenseRepository, InvoiceRepository


from domain.entities.finance import SavingsDeposit
from domain.repositories.finance import SavingsDepositRepository


class InMemorySavingsDepositRepository(SavingsDepositRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, SavingsDeposit] = {}

    def get_by_id(self, deposit_id: UUID) -> SavingsDeposit | None:
        return self._store.get(deposit_id)

    def save(self, deposit: SavingsDeposit) -> None:
        self._store[deposit.id] = deposit

    def delete(self, deposit_id: UUID) -> None:
        self._store.pop(deposit_id, None)

    def list_by_goal(self, goal_id: UUID) -> list[SavingsDeposit]:
        return [d for d in self._store.values() if d.goal_id == goal_id]

    def get_monthly_savings_usd(self, user_id: UUID, year: int, month: int) -> "Decimal":
        from decimal import Decimal
        return sum(
            (d.amount for d in self._store.values()
             if d.user_id == user_id and d.date.year == year and d.date.month == month),
            Decimal("0"),
        )

    def get_total_deposited_usd(self, goal_id: UUID) -> "Decimal":
        from decimal import Decimal
        from domain.entities.finance import Currency
        return sum(
            (d.amount for d in self._store.values()
             if d.goal_id == goal_id and d.currency == Currency.USD),
            Decimal("0"),
        )

    def get_monthly_deposits_by_goal(
        self, user_id: UUID, year: int, month: int
    ) -> list[tuple[UUID, "Decimal"]]:
        from decimal import Decimal
        from collections import defaultdict
        totals: dict[UUID, Decimal] = defaultdict(Decimal)
        for d in self._store.values():
            if d.user_id == user_id and d.date.year == year and d.date.month == month:
                totals[d.goal_id] += d.amount
        return list(totals.items())


class InMemoryInvoiceRepository(InvoiceRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Invoice] = {}

    def get_by_id(self, invoice_id: UUID) -> Invoice | None:
        return self._store.get(invoice_id)

    def save(self, invoice: Invoice) -> None:
        self._store[invoice.id] = invoice

    def list_by_user(self, user_id: UUID) -> list[Invoice]:
        return [i for i in self._store.values() if i.user_id == user_id]

    def list_unpaid(self) -> list[Invoice]:
        return [i for i in self._store.values() if not i.is_paid]

    def list_unpaid_by_user(self, user_id: UUID) -> list[Invoice]:
        return sorted(
            [i for i in self._store.values() if not i.is_paid and i.user_id == user_id],
            key=lambda x: x.due_date,
        )

    def list_all(self) -> list[Invoice]:
        return list(self._store.values())


class InMemoryExpenseRepository(ExpenseRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Expense] = {}

    def get_by_id(self, expense_id: UUID) -> Expense | None:
        return self._store.get(expense_id)

    def save(self, expense: Expense) -> None:
        self._store[expense.id] = expense

    def list_by_period(self, year: int, month: int) -> list[Expense]:
        return [e for e in self._store.values() if e.date.year == year and e.date.month == month]

    def list_by_category(self, category: str) -> list[Expense]:
        return [e for e in self._store.values() if e.category == category]

    def list_between_dates(self, start: date, end: date) -> list[Expense]:
        return [e for e in self._store.values() if start <= e.date <= end]
