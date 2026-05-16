from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import EditTransactionCommand, TransactionEditedResponse
from application.use_cases.finance.edit_transaction import EditTransactionUseCase
from domain.entities.finance import Transaction, TransactionType
from domain.entities.user import User
from domain.exceptions.finance import (
    InvalidEditionCredentialsError,
    TransactionNotFoundError,
    UnauthorizedEditError,
)
from domain.repositories.finance import TransactionRepository
from domain.repositories.user import PasswordHasher, UserRepository


class TestEditTransactionUseCase:
    def setup_method(self):
        self.transaction_repo = MagicMock(spec=TransactionRepository)
        self.user_repo = MagicMock(spec=UserRepository)
        self.password_hasher = MagicMock(spec=PasswordHasher)
        self.sut = EditTransactionUseCase(
            transaction_repo=self.transaction_repo,
            user_repo=self.user_repo,
            password_hasher=self.password_hasher,
        )
        self.user_id = uuid4()
        self.transaction_id = uuid4()
        self.tx = Transaction(
            id=self.transaction_id,
            user_id=self.user_id,
            account_id=uuid4(),
            type=TransactionType.EXPENSE,
            amount=Decimal("100.00"),
            currency="USD",
            exchange_rate=Decimal("1.0"),
            date="2025-01-15",
            notes="Old notes",
        )
        self.transaction_repo.get_by_id.return_value = self.tx
        self.user = User(
            id=self.user_id,
            first_name="Test",
            last_name="User",
            email="test@example.com",
            hashed_password="hashed_secret",
            is_admin=False,
        )
        self.user_repo.get_by_id.return_value = self.user
        self.password_hasher.verify.return_value = True

    def test_should_update_notes_when_credentials_are_valid(self):
        command = EditTransactionCommand(
            transaction_id=self.transaction_id,
            user_id=self.user_id,
            notes="Updated notes",
            password="correct_password",
        )

        result = self.sut.execute(command)

        assert isinstance(result, TransactionEditedResponse)
        assert result.transaction_id == self.transaction_id
        assert result.notes == "Updated notes"
        self.transaction_repo.save.assert_called_once()

    def test_should_raise_not_found_when_transaction_does_not_exist(self):
        self.transaction_repo.get_by_id.return_value = None
        command = EditTransactionCommand(
            transaction_id=uuid4(),
            user_id=self.user_id,
            notes="Test",
            password="password",
        )

        with pytest.raises(TransactionNotFoundError):
            self.sut.execute(command)

    def test_should_raise_unauthorized_when_user_does_not_own_transaction(self):
        other_user_id = uuid4()
        command = EditTransactionCommand(
            transaction_id=self.transaction_id,
            user_id=other_user_id,
            notes="Test",
            password="password",
        )

        with pytest.raises(UnauthorizedEditError):
            self.sut.execute(command)

    def test_should_raise_invalid_credentials_when_password_is_wrong(self):
        self.password_hasher.verify.return_value = False
        command = EditTransactionCommand(
            transaction_id=self.transaction_id,
            user_id=self.user_id,
            notes="Test",
            password="wrong_password",
        )

        with pytest.raises(InvalidEditionCredentialsError):
            self.sut.execute(command)

    def test_should_raise_invalid_credentials_when_user_not_found(self):
        self.user_repo.get_by_id.return_value = None
        command = EditTransactionCommand(
            transaction_id=self.transaction_id,
            user_id=self.user_id,
            notes="Test",
            password="password",
        )

        with pytest.raises(InvalidEditionCredentialsError):
            self.sut.execute(command)

    # --- Currency change ---

    def test_should_update_currency_when_provided(self):
        from domain.entities.finance import Currency

        command = EditTransactionCommand(
            transaction_id=self.transaction_id,
            user_id=self.user_id,
            password="correct_password",
            currency=Currency.VES,
        )

        result = self.sut.execute(command)

        assert result.currency == Currency.VES
        saved_tx = self.transaction_repo.save.call_args[0][0]
        assert saved_tx.currency == Currency.VES

    def test_currency_change_does_not_cascade_to_exchange_pair(self):
        """Changing currency on one side of an exchange pair must NOT touch the other side,
        since each side holds a different currency by design."""
        from domain.entities.finance import Currency

        tx_in_id = uuid4()
        tx_out = Transaction(
            id=self.transaction_id,
            user_id=self.user_id,
            account_id=uuid4(),
            type=TransactionType.EXCHANGE_OUT,
            amount=Decimal("100.00"),
            currency=Currency.VES,
            exchange_rate=Decimal("36.00"),
            date="2025-01-15",
            related_transaction_id=tx_in_id,
        )
        tx_in = Transaction(
            id=tx_in_id,
            user_id=self.user_id,
            account_id=uuid4(),
            type=TransactionType.EXCHANGE_IN,
            amount=Decimal("3600.00"),
            currency=Currency.USD,
            exchange_rate=Decimal("36.00"),
            date="2025-01-15",
            related_transaction_id=self.transaction_id,
        )
        self.transaction_repo.get_by_id.side_effect = lambda tid: (
            tx_out if tid == tx_out.id else tx_in
        )

        command = EditTransactionCommand(
            transaction_id=tx_out.id,
            user_id=self.user_id,
            password="correct_password",
            currency=Currency.USDT,  # change OUT currency only
        )
        self.sut.execute(command)

        # Only OUT is saved — currency changes never cascade
        self.transaction_repo.save.assert_called_once()
        saved_out = self.transaction_repo.save.call_args[0][0]
        assert saved_out.currency == Currency.USDT

    def test_response_always_includes_currency(self):
        from domain.entities.finance import Currency

        command = EditTransactionCommand(
            transaction_id=self.transaction_id,
            user_id=self.user_id,
            password="correct_password",
            notes="just notes",
        )

        result = self.sut.execute(command)

        # Currency not changed → response still carries the original currency
        assert result.currency == Currency.USD

    # --- F1: Exchange pair cascade ---

    def _make_exchange_pair(self):
        """Return (tx_out, tx_in) linked by related_transaction_id."""
        tx_in_id = uuid4()
        tx_out = Transaction(
            id=self.transaction_id,
            user_id=self.user_id,
            account_id=uuid4(),
            type=TransactionType.EXCHANGE_OUT,
            amount=Decimal("100.00"),
            currency="VES",
            exchange_rate=Decimal("36.00"),
            date="2025-01-15",
            related_transaction_id=tx_in_id,
        )
        tx_in = Transaction(
            id=tx_in_id,
            user_id=self.user_id,
            account_id=uuid4(),
            type=TransactionType.EXCHANGE_IN,
            amount=Decimal("3600.00"),
            currency="USD",
            exchange_rate=Decimal("36.00"),
            date="2025-01-15",
            related_transaction_id=self.transaction_id,
        )
        return tx_out, tx_in

    def test_editing_exchange_out_amount_recalculates_exchange_in_amount(self):
        tx_out, tx_in = self._make_exchange_pair()
        self.transaction_repo.get_by_id.side_effect = lambda tid: (
            tx_out if tid == tx_out.id else tx_in
        )

        command = EditTransactionCommand(
            transaction_id=tx_out.id,
            user_id=self.user_id,
            password="correct_password",
            amount=Decimal("200.00"),  # double the amount
        )
        self.sut.execute(command)

        # save called twice: once for OUT, once for IN
        assert self.transaction_repo.save.call_count == 2
        saved_in = self.transaction_repo.save.call_args_list[1][0][0]
        # amount_in = amount_out * rate = 200 * 36 = 7200
        assert saved_in.amount == Decimal("7200.00")

    def test_editing_exchange_out_rate_recalculates_exchange_in_amount(self):
        tx_out, tx_in = self._make_exchange_pair()
        self.transaction_repo.get_by_id.side_effect = lambda tid: (
            tx_out if tid == tx_out.id else tx_in
        )

        command = EditTransactionCommand(
            transaction_id=tx_out.id,
            user_id=self.user_id,
            password="correct_password",
            exchange_rate=Decimal("40.00"),
        )
        self.sut.execute(command)

        assert self.transaction_repo.save.call_count == 2
        saved_in = self.transaction_repo.save.call_args_list[1][0][0]
        # amount_in = amount_out * new_rate = 100 * 40 = 4000
        assert saved_in.amount == Decimal("4000.00")
        assert saved_in.exchange_rate == Decimal("40.00")

    def test_editing_regular_expense_does_not_cascade(self):
        """EXPENSE transactions have no related pair — only one save."""
        command = EditTransactionCommand(
            transaction_id=self.transaction_id,
            user_id=self.user_id,
            password="correct_password",
            amount=Decimal("50.00"),
        )
        self.sut.execute(command)

        self.transaction_repo.save.assert_called_once()

    def test_cascade_skipped_when_related_tx_not_found(self):
        tx_out, _ = self._make_exchange_pair()
        # OUT exists, but IN is missing in repo
        self.transaction_repo.get_by_id.side_effect = lambda tid: (
            tx_out if tid == tx_out.id else None
        )

        command = EditTransactionCommand(
            transaction_id=tx_out.id,
            user_id=self.user_id,
            password="correct_password",
            amount=Decimal("150.00"),
        )
        # Should not raise; only OUT is saved
        self.sut.execute(command)
        self.transaction_repo.save.assert_called_once()
