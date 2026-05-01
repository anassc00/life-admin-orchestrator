"""Shared test fixtures.

Unit tests use in-memory repository fakes — the Django ORM is never exercised.
Integration tests use pytest-django and a real (test) PostgreSQL database.
"""

import pytest

from tests.fakes.repositories import (
    InMemoryAppointmentRepository,
    InMemoryContactRepository,
    InMemoryDocumentRepository,
    InMemoryExpenseRepository,
    InMemoryInteractionRepository,
    InMemoryInvoiceRepository,
)

# --- Finance fakes ---


@pytest.fixture
def invoice_repo() -> InMemoryInvoiceRepository:
    return InMemoryInvoiceRepository()


@pytest.fixture
def expense_repo() -> InMemoryExpenseRepository:
    return InMemoryExpenseRepository()


# --- Calendar fakes ---


@pytest.fixture
def appointment_repo() -> InMemoryAppointmentRepository:
    return InMemoryAppointmentRepository()


# --- Document fakes ---


@pytest.fixture
def document_repo() -> InMemoryDocumentRepository:
    return InMemoryDocumentRepository()


# --- Contact fakes ---


@pytest.fixture
def contact_repo() -> InMemoryContactRepository:
    return InMemoryContactRepository()


@pytest.fixture
def interaction_repo() -> InMemoryInteractionRepository:
    return InMemoryInteractionRepository()
