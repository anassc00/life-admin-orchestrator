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
