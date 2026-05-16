"""In-memory repository implementations for unit testing.

These satisfy the domain repository interfaces without touching
the database, so use cases can be tested in complete isolation.
"""

from datetime import date
from uuid import UUID

from domain.entities.finance import Expense, Invoice
from domain.repositories.finance import ExpenseRepository, InvoiceRepository


class InMemoryInvoiceRepository(InvoiceRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Invoice] = {}

    def get_by_id(self, invoice_id: UUID) -> Invoice | None:
        return self._store.get(invoice_id)

    def save(self, invoice: Invoice) -> None:
        self._store[invoice.id] = invoice

    def list_unpaid(self) -> list[Invoice]:
        return [i for i in self._store.values() if not i.is_paid]

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
