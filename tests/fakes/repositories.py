"""In-memory repository implementations for unit testing.

These satisfy the domain repository interfaces without touching
the database, so use cases can be tested in complete isolation.
"""
from datetime import date, datetime
from uuid import UUID

from domain.entities.calendar import Appointment
from domain.entities.contact import Contact, Interaction
from domain.entities.document import Document, DocumentStatus
from domain.entities.finance import Expense, Invoice
from domain.repositories.calendar import AppointmentRepository
from domain.repositories.contact import ContactRepository, InteractionRepository
from domain.repositories.document import DocumentRepository
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


class InMemoryAppointmentRepository(AppointmentRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Appointment] = {}

    def get_by_id(self, appointment_id: UUID) -> Appointment | None:
        return self._store.get(appointment_id)

    def save(self, appointment: Appointment) -> None:
        self._store[appointment.id] = appointment

    def list_by_range(self, start: datetime, end: datetime) -> list[Appointment]:
        return [
            a for a in self._store.values()
            if a.start_time < end and a.end_time > start
        ]

    def delete(self, appointment_id: UUID) -> None:
        self._store.pop(appointment_id, None)


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Document] = {}

    def get_by_id(self, document_id: UUID) -> Document | None:
        return self._store.get(document_id)

    def save(self, document: Document) -> None:
        self._store[document.id] = document

    def list_by_status(self, status: DocumentStatus) -> list[Document]:
        return [d for d in self._store.values() if d.status == status]

    def list_by_category(self, category: str) -> list[Document]:
        return [d for d in self._store.values() if d.category == category]


class InMemoryContactRepository(ContactRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Contact] = {}

    def get_by_id(self, contact_id: UUID) -> Contact | None:
        return self._store.get(contact_id)

    def save(self, contact: Contact) -> None:
        self._store[contact.id] = contact

    def list_all(self) -> list[Contact]:
        return list(self._store.values())

    def search(self, query: str) -> list[Contact]:
        q = query.lower()
        return [
            c for c in self._store.values()
            if q in c.name.lower() or q in c.email.lower() or q in c.company.lower()
        ]


class InMemoryInteractionRepository(InteractionRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Interaction] = {}

    def save(self, interaction: Interaction) -> None:
        self._store[interaction.id] = interaction

    def list_by_contact(self, contact_id: UUID) -> list[Interaction]:
        return [i for i in self._store.values() if i.contact_id == contact_id]
