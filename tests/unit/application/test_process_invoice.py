import pytest
from decimal import Decimal
from datetime import date
from uuid import uuid4

from application.dtos.finance import CreateInvoiceCommand, ProcessInvoiceCommand
from application.use_cases.finance.create_invoice import CreateInvoiceUseCase
from application.use_cases.finance.process_invoice import ProcessInvoiceUseCase
from domain.exceptions.finance import InvoiceAlreadyPaidError, InvoiceNotFoundError
from tests.fakes.repositories import InMemoryInvoiceRepository


@pytest.fixture
def repo() -> InMemoryInvoiceRepository:
    return InMemoryInvoiceRepository()


class TestCreateInvoiceUseCase:
    def test_creates_and_persists_invoice(self, repo: InMemoryInvoiceRepository):
        uc = CreateInvoiceUseCase(invoice_repo=repo)
        command = CreateInvoiceCommand(
            vendor="Telmex",
            amount=Decimal("599.00"),
            due_date=date(2026, 5, 15),
        )
        response = uc.execute(command)

        assert response.status == "created"
        assert response.vendor == "Telmex"
        assert repo.get_by_id(response.invoice_id) is not None


class TestProcessInvoiceUseCase:
    def test_marks_invoice_as_paid(self, repo: InMemoryInvoiceRepository):
        create_uc = CreateInvoiceUseCase(invoice_repo=repo)
        created = create_uc.execute(
            CreateInvoiceCommand(
                vendor="CFE",
                amount=Decimal("1200.00"),
                due_date=date(2026, 5, 10),
            )
        )

        process_uc = ProcessInvoiceUseCase(invoice_repo=repo)
        response = process_uc.execute(ProcessInvoiceCommand(invoice_id=created.invoice_id))

        assert response.status == "paid"
        assert repo.get_by_id(created.invoice_id).is_paid is True

    def test_raises_when_invoice_not_found(self, repo: InMemoryInvoiceRepository):
        uc = ProcessInvoiceUseCase(invoice_repo=repo)
        with pytest.raises(InvoiceNotFoundError):
            uc.execute(ProcessInvoiceCommand(invoice_id=uuid4()))

    def test_raises_when_already_paid(self, repo: InMemoryInvoiceRepository):
        create_uc = CreateInvoiceUseCase(invoice_repo=repo)
        created = create_uc.execute(
            CreateInvoiceCommand(
                vendor="Izzi",
                amount=Decimal("450.00"),
                due_date=date(2026, 5, 10),
            )
        )
        process_uc = ProcessInvoiceUseCase(invoice_repo=repo)
        process_uc.execute(ProcessInvoiceCommand(invoice_id=created.invoice_id))

        with pytest.raises(InvoiceAlreadyPaidError):
            process_uc.execute(ProcessInvoiceCommand(invoice_id=created.invoice_id))
