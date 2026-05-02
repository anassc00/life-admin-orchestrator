"""Unit tests for exchange math validation and InvalidEditionCredentialsError."""

import datetime
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import (
    EditTransactionCommand,
    RegisterCurrencyExchangeCommand,
)
from application.use_cases.finance.edit_transaction import EditTransactionUseCase
from application.use_cases.finance.register_currency_exchange import RegisterCurrencyExchangeUseCase
from domain.entities.finance import Currency, IncomeCategory, Transaction, TransactionType
from domain.exceptions.finance import (
    InvalidEditionCredentialsError,
    InvalidExchangeMathError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TODAY = datetime.date(2026, 5, 1)


def _exchange_command(amount_out, amount_in, rate, user_id, out_id, in_id):
    return RegisterCurrencyExchangeCommand(
        user_id=user_id,
        source_account_id=out_id,
        dest_account_id=in_id,
        amount_out=amount_out,
        currency_out=Currency.USD,
        amount_in=amount_in,
        currency_in=Currency.VES,
        exchange_rate=rate,
        date=_TODAY,
    )


def _make_exchange_uc():
    account_repo = MagicMock()
    tx_repo = MagicMock()
    out_id = uuid4()
    in_id = uuid4()
    user_id = uuid4()

    out_account = MagicMock()
    out_account.user_id = user_id
    in_account = MagicMock()
    in_account.user_id = user_id

    def get_by_id(account_id):
        if account_id == out_id:
            return out_account
        if account_id == in_id:
            return in_account
        return None

    account_repo.get_by_id.side_effect = get_by_id
    uc = RegisterCurrencyExchangeUseCase(account_repo=account_repo, transaction_repo=tx_repo)
    return uc, tx_repo, user_id, out_id, in_id


def _make_tx(user_id):
    return Transaction(
        user_id=user_id,
        account_id=uuid4(),
        type=TransactionType.INCOME,
        amount=Decimal("500"),
        currency=Currency.USD,
        exchange_rate=Decimal("1.0"),
        category=IncomeCategory.SALARY,
        date=_TODAY,
    )


def _make_edit_uc():
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
    return uc, tx_repo, password_hasher


# ---------------------------------------------------------------------------
# RegisterCurrencyExchangeUseCase — Math validation
# ---------------------------------------------------------------------------


class TestRegisterCurrencyExchangeMathValidation:
    def test_accepts_exact_math(self):
        """100 USD × 36 = 3600 VES — passes."""
        uc, tx_repo, user_id, out_id, in_id = _make_exchange_uc()
        cmd = _exchange_command(Decimal("100"), Decimal("3600"), Decimal("36"), user_id, out_id, in_id)
        uc.execute(cmd)
        tx_repo.save_exchange_pair.assert_called_once()

    def test_accepts_math_within_1pct_tolerance(self):
        """100 USD × 36 = 3600 but user typed 3596 (0.11% deviation) — passes."""
        uc, tx_repo, user_id, out_id, in_id = _make_exchange_uc()
        cmd = _exchange_command(Decimal("100"), Decimal("3596"), Decimal("36"), user_id, out_id, in_id)
        uc.execute(cmd)
        tx_repo.save_exchange_pair.assert_called_once()

    def test_raises_when_math_is_wrong(self):
        """100 USD × 36 = 3600 but user typed 4000 (11% deviation) — fails."""
        uc, tx_repo, user_id, out_id, in_id = _make_exchange_uc()
        cmd = _exchange_command(Decimal("100"), Decimal("4000"), Decimal("36"), user_id, out_id, in_id)
        with pytest.raises(InvalidExchangeMathError):
            uc.execute(cmd)
        tx_repo.save_exchange_pair.assert_not_called()

    def test_raises_when_amount_in_is_zero_but_rate_is_positive(self):
        """0 received for 100 sent — clearly wrong."""
        uc, tx_repo, user_id, out_id, in_id = _make_exchange_uc()
        cmd = _exchange_command(Decimal("100"), Decimal("0.01"), Decimal("36"), user_id, out_id, in_id)
        with pytest.raises(InvalidExchangeMathError):
            uc.execute(cmd)
        tx_repo.save_exchange_pair.assert_not_called()


# ---------------------------------------------------------------------------
# EditTransactionUseCase — InvalidEditionCredentialsError
# ---------------------------------------------------------------------------


class TestEditTransactionInvalidEditionCredentials:
    def test_raises_invalid_edition_credentials_error_when_password_is_wrong(self):
        uc, tx_repo, password_hasher = _make_edit_uc()
        user_id = uuid4()
        tx = _make_tx(user_id)
        tx_repo.get_by_id.return_value = tx
        password_hasher.verify.return_value = False

        with pytest.raises(InvalidEditionCredentialsError):
            uc.execute(
                EditTransactionCommand(
                    user_id=user_id,
                    transaction_id=tx.id,
                    password="wrong",
                    notes="updated note",
                )
            )
        tx_repo.save.assert_not_called()

    def test_raises_invalid_edition_credentials_error_when_user_not_found(self):
        uc, tx_repo, password_hasher = _make_edit_uc()
        user_id = uuid4()
        tx = _make_tx(user_id)
        tx_repo.get_by_id.return_value = tx

        # Simulate user deleted from DB
        from unittest.mock import patch
        with patch.object(uc, '_user_repo') as mock_user_repo:
            mock_user_repo.get_by_id.return_value = None
            with pytest.raises(InvalidEditionCredentialsError):
                uc.execute(
                    EditTransactionCommand(
                        user_id=user_id,
                        transaction_id=tx.id,
                        password="any",
                        notes="note",
                    )
                )
