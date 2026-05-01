from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import EditTransactionCommand, TransactionEditedResponse
from application.use_cases.finance.edit_transaction import EditTransactionUseCase
from domain.entities.finance import Currency, IncomeCategory, Transaction, TransactionType
from domain.exceptions.finance import TransactionNotFoundError, UnauthorizedEditError
from domain.exceptions.user import InvalidCredentialsError


class TestEditTransactionUseCase:
    def _make_uc(self) -> tuple[EditTransactionUseCase, MagicMock, MagicMock, MagicMock]:
        tx_repo = MagicMock()
        user_repo = MagicMock()
        password_hasher = MagicMock()
        password_hasher.verify.return_value = True

        user = MagicMock()
        user.hashed_password = "hashed"
        user_repo.get_by_id.return_value = user

        uc = EditTransactionUseCase(
            transaction_repo=tx_repo,
            user_repo=user_repo,
            password_hasher=password_hasher,
        )
        return uc, tx_repo, user_repo, password_hasher

    def _make_tx(self, user_id) -> Transaction:
        return Transaction(
            user_id=user_id,
            account_id=uuid4(),
            type=TransactionType.INCOME,
            amount=Decimal("500"),
            currency=Currency.USD,
            exchange_rate=Decimal("1.0"),
            category=IncomeCategory.SALARY,
            date=date(2026, 4, 27),
        )

    def test_edits_transaction_notes_with_valid_password(self) -> None:
        uc, tx_repo, user_repo, _ = self._make_uc()
        user_id = uuid4()
        tx = self._make_tx(user_id)
        tx_repo.get_by_id.return_value = tx

        result = uc.execute(
            EditTransactionCommand(
                user_id=user_id,
                transaction_id=tx.id,
                password="correct_password",
                notes="Updated note",
            )
        )

        assert isinstance(result, TransactionEditedResponse)
        tx_repo.save.assert_called_once()

    def test_raises_if_transaction_not_found(self) -> None:
        uc, tx_repo, user_repo, _ = self._make_uc()
        tx_repo.get_by_id.return_value = None

        with pytest.raises(TransactionNotFoundError):
            uc.execute(
                EditTransactionCommand(
                    user_id=uuid4(),
                    transaction_id=uuid4(),
                    password="pass",
                    notes="note",
                )
            )

    def test_raises_if_transaction_belongs_to_another_user(self) -> None:
        uc, tx_repo, user_repo, _ = self._make_uc()
        tx = self._make_tx(user_id=uuid4())
        tx_repo.get_by_id.return_value = tx
        other_user_id = uuid4()

        with pytest.raises(UnauthorizedEditError):
            uc.execute(
                EditTransactionCommand(
                    user_id=other_user_id,
                    transaction_id=tx.id,
                    password="pass",
                    notes="note",
                )
            )

    def test_raises_if_password_is_wrong(self) -> None:
        uc, tx_repo, user_repo, password_hasher = self._make_uc()
        user_id = uuid4()
        tx = self._make_tx(user_id)
        tx_repo.get_by_id.return_value = tx
        password_hasher.verify.return_value = False

        with pytest.raises(InvalidCredentialsError):
            uc.execute(
                EditTransactionCommand(
                    user_id=user_id,
                    transaction_id=tx.id,
                    password="wrong_password",
                    notes="note",
                )
            )
