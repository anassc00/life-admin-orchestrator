from datetime import date
from decimal import Decimal

import pytest

from domain.entities.finance import Expense, Invoice


class TestInvoice:
    def test_invoice_creation_defaults(self):
        invoice = Invoice(
            vendor="Acme",
            amount=Decimal("1500.00"),
            due_date=date(2026, 5, 1),
        )
        assert invoice.currency == "MXN"
        assert invoice.is_paid is False
        assert invoice.id is not None

    def test_mark_as_paid_returns_new_instance(self):
        invoice = Invoice(
            vendor="Acme",
            amount=Decimal("1500.00"),
            due_date=date(2026, 5, 1),
        )
        paid = invoice.mark_as_paid()

        assert paid.is_paid is True
        assert invoice.is_paid is False  # original is unchanged (frozen)
        assert paid.id == invoice.id

    def test_invoice_is_frozen(self):
        invoice = Invoice(
            vendor="Acme",
            amount=Decimal("500.00"),
            due_date=date(2026, 5, 1),
        )
        with pytest.raises(Exception):
            invoice.is_paid = True  # type: ignore[misc]


class TestExpense:
    def test_expense_creation(self):
        expense = Expense(
            description="Electricity bill",
            amount=Decimal("800.00"),
            category="utilities",
            date=date(2026, 4, 15),
        )
        assert expense.currency == "MXN"
        assert expense.invoice_id is None
