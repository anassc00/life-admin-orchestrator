from decimal import Decimal
from unittest.mock import MagicMock, call
from uuid import uuid4

import pytest

from application.dtos.finance import DeleteTransactionCommand
from application.use_cases.finance.delete_transaction import DeleteTransactionUseCase
from domain.entities.finance import Currency, Transaction, TransactionType
from domain.exceptions.finance import (
    InvalidEditionCredentialsError,
    TransactionNotFoundError,
    UnauthorizedEditError,
)


class TestDeleteTransactionUseCase:
    def _make_uc(self):
        tx_repo = MagicMock()
        user_repo = MagicMock()
        password_hasher = MagicMock()
        password_hasher.verify.return_value = True

        user = MagicMock()
        user.hashed_password = "hashed"
        user_repo.get_by_id.return_value = user

        uc = DeleteTransactionUseCase(
            transaction_repo=tx_repo,
            user_repo=user_repo,
            password_hasher=password_hasher,
        )
        return uc, tx_repo, user_repo, password_hasher

    def _make_tx(self, user_id, tx_type=TransactionType.EXPENSE, related_id=None):
        return Transaction(
            id=uuid4(),
            user_id=user_id,
            account_id=uuid4(),
            type=tx_type,
            amount=Decimal("100.00"),
            currency=Currency.USD,
            exchange_rate=Decimal("1"),
            date=__import__("datetime").date(2026, 5, 1),
            related_transaction_id=related_id,
        )

    # --- Happy path: single transaction ---

    def test_deletes_single_transaction(self):
        uc, tx_repo, user_repo, _ = self._make_uc()
        user_id = uuid4()
        tx = self._make_tx(user_id)
        tx_repo.get_by_id.return_value = tx

        cmd = DeleteTransactionCommand(
            user_id=user_id, transaction_id=tx.id, password="secret"
        )
        result = uc.execute(cmd)

        tx_repo.delete.assert_called_once_with(tx.id)
        tx_repo.delete_pair.assert_not_called()
        assert result.transaction_id == tx.id
        assert result.related_transaction_id is None

    # --- Happy path: exchange pair ---

    def test_deletes_exchange_pair_atomically(self):
        uc, tx_repo, _, _ = self._make_uc()
        user_id = uuid4()
        related_id = uuid4()
        tx = self._make_tx(user_id, TransactionType.EXCHANGE_OUT, related_id=related_id)
        tx_repo.get_by_id.return_value = tx

        cmd = DeleteTransactionCommand(
            user_id=user_id, transaction_id=tx.id, password="secret"
        )
        result = uc.execute(cmd)

        tx_repo.delete_pair.assert_called_once_with(tx.id, related_id)
        tx_repo.delete.assert_not_called()
        assert result.transaction_id == tx.id
        assert result.related_transaction_id == related_id

    # --- Error: transaction not found ---

    def test_raises_when_transaction_not_found(self):
        uc, tx_repo, _, _ = self._make_uc()
        tx_repo.get_by_id.return_value = None
        cmd = DeleteTransactionCommand(
            user_id=uuid4(), transaction_id=uuid4(), password="secret"
        )
        with pytest.raises(TransactionNotFoundError):
            uc.execute(cmd)

    # --- Error: transaction belongs to different user ---

    def test_raises_when_transaction_belongs_to_other_user(self):
        uc, tx_repo, _, _ = self._make_uc()
        tx = self._make_tx(user_id=uuid4())
        tx_repo.get_by_id.return_value = tx

        cmd = DeleteTransactionCommand(
            user_id=uuid4(),  # different user
            transaction_id=tx.id,
            password="secret",
        )
        with pytest.raises(UnauthorizedEditError):
            uc.execute(cmd)

    # --- Error: wrong password ---

    def test_raises_when_password_is_wrong(self):
        uc, tx_repo, _, password_hasher = self._make_uc()
        password_hasher.verify.return_value = False
        user_id = uuid4()
        tx = self._make_tx(user_id)
        tx_repo.get_by_id.return_value = tx

        cmd = DeleteTransactionCommand(
            user_id=user_id, transaction_id=tx.id, password="wrong"
        )
        with pytest.raises(InvalidEditionCredentialsError):
            uc.execute(cmd)
        tx_repo.delete.assert_not_called()

    # --- Error: user not found ---

    def test_raises_when_user_not_found(self):
        uc, tx_repo, user_repo, _ = self._make_uc()
        user_repo.get_by_id.return_value = None
        user_id = uuid4()
        tx = self._make_tx(user_id)
        tx_repo.get_by_id.return_value = tx

        cmd = DeleteTransactionCommand(
            user_id=user_id, transaction_id=tx.id, password="secret"
        )
        with pytest.raises(InvalidEditionCredentialsError):
            uc.execute(cmd)
        tx_repo.delete.assert_not_called()
