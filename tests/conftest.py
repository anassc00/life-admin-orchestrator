"""Shared test fixtures.

Unit tests use in-memory repository fakes — the Django ORM is never exercised.
Integration tests use pytest-django and a real (test) PostgreSQL database.
"""

import pytest

from tests.fakes.repositories import (
    InMemoryExpenseRepository,
    InMemoryInvoiceRepository,
)

# --- Finance fakes ---


@pytest.fixture
def invoice_repo() -> InMemoryInvoiceRepository:
    return InMemoryInvoiceRepository()


@pytest.fixture
def expense_repo() -> InMemoryExpenseRepository:
    return InMemoryExpenseRepository()
