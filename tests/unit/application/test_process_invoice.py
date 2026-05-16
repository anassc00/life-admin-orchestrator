from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import CreateInvoiceCommand, ProcessInvoiceCommand
from application.use_cases.finance.create_invoice import CreateInvoiceUseCase
from application.use_cases.finance.process_invoice import ProcessInvoiceUseCase
from domain.entities.finance import TransactionType
from domain.exceptions.finance import InvoiceAlreadyPaidError, InvoiceNotFoundError
from domain.repositories.finance import TransactionRepository
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

    # --- F5: expense transaction creation ---

    def test_creates_expense_transaction_when_account_context_provided(
        self, repo: InMemoryInvoiceRepository
    ):
        tx_repo = MagicMock(spec=TransactionRepository)
        create_uc = CreateInvoiceUseCase(invoice_repo=repo)
        created = create_uc.execute(
            CreateInvoiceCommand(
                vendor="Telmex",
                amount=Decimal("599.00"),
                currency="MXN",
                due_date=date(2026, 5, 15),
            )
        )

        user_id = uuid4()
        account_id = uuid4()
        process_uc = ProcessInvoiceUseCase(invoice_repo=repo, transaction_repo=tx_repo)
        result = process_uc.execute(
            ProcessInvoiceCommand(
                invoice_id=created.invoice_id,
                user_id=user_id,
                account_id=account_id,
                exchange_rate=Decimal("17.50"),
            )
        )

        assert result.status == "paid"
        assert result.transaction_id is not None
        tx_repo.save.assert_called_once()
        saved_tx = tx_repo.save.call_args[0][0]
        assert saved_tx.type == TransactionType.EXPENSE
        assert saved_tx.amount == Decimal("599.00")
        assert saved_tx.user_id == user_id
        assert saved_tx.account_id == account_id
        assert "Telmex" in saved_tx.description

    def test_no_transaction_created_without_account_context(
        self, repo: InMemoryInvoiceRepository
    ):
        tx_repo = MagicMock(spec=TransactionRepository)
        create_uc = CreateInvoiceUseCase(invoice_repo=repo)
        created = create_uc.execute(
            CreateInvoiceCommand(
                vendor="CFE",
                amount=Decimal("300.00"),
                due_date=date(2026, 5, 20),
            )
        )

        process_uc = ProcessInvoiceUseCase(invoice_repo=repo, transaction_repo=tx_repo)
        result = process_uc.execute(
            ProcessInvoiceCommand(invoice_id=created.invoice_id)  # no user_id/account_id
        )

        assert result.status == "paid"
        assert result.transaction_id is None
        tx_repo.save.assert_not_called()

    def test_no_transaction_created_without_transaction_repo(
        self, repo: InMemoryInvoiceRepository
    ):
        create_uc = CreateInvoiceUseCase(invoice_repo=repo)
        created = create_uc.execute(
            CreateInvoiceCommand(
                vendor="Izzi",
                amount=Decimal("450.00"),
                due_date=date(2026, 5, 10),
            )
        )

        process_uc = ProcessInvoiceUseCase(invoice_repo=repo)  # no tx_repo
        result = process_uc.execute(
            ProcessInvoiceCommand(
                invoice_id=created.invoice_id,
                user_id=uuid4(),
                account_id=uuid4(),
            )
        )

        assert result.status == "paid"
        assert result.transaction_id is None
