"""Verifies that income and exchange use cases enforce account ownership."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import RegisterCurrencyExchangeCommand, RegisterIncomeCommand
from application.use_cases.finance.register_currency_exchange import RegisterCurrencyExchangeUseCase
from application.use_cases.finance.register_income import RegisterIncomeUseCase
from domain.entities.finance import Account, AccountType, Currency, IncomeCategory
from domain.exceptions.finance import AccountAccessForbiddenError


def _make_account(user_id) -> Account:
    return Account(
        user_id=user_id,
        name="Test",
        type=AccountType.WALLET,
        supported_currencies=[Currency.USD],
        default_currencies=[Currency.USD],
    )


class TestIncomeOwnershipEnforcement:
    def test_raises_if_account_belongs_to_another_user(self) -> None:
        account_repo = MagicMock()
        tx_repo = MagicMock()
        owner_id = uuid4()
        account = _make_account(owner_id)
        account_repo.get_by_id.return_value = account

        uc = RegisterIncomeUseCase(account_repo=account_repo, transaction_repo=tx_repo)

        with pytest.raises(AccountAccessForbiddenError):
            uc.execute(
                RegisterIncomeCommand(
                    user_id=uuid4(),  # different user — not the owner
                    account_id=account.id,
                    amount=Decimal("100"),
                    currency=Currency.USD,
                    exchange_rate=Decimal("1.0"),
                    category=IncomeCategory.SALARY,
                    date=date(2026, 5, 1),
                )
            )

    def test_allows_owner_to_register_income(self) -> None:
        account_repo = MagicMock()
        tx_repo = MagicMock()
        user_id = uuid4()
        account = _make_account(user_id)
        account_repo.get_by_id.return_value = account

        uc = RegisterIncomeUseCase(account_repo=account_repo, transaction_repo=tx_repo)
        result = uc.execute(
            RegisterIncomeCommand(
                user_id=user_id,
                account_id=account.id,
                amount=Decimal("500"),
                currency=Currency.USD,
                exchange_rate=Decimal("1.0"),
                category=IncomeCategory.SALARY,
                date=date(2026, 5, 1),
            )
        )

        assert result.amount == Decimal("500")


class TestExchangeOwnershipEnforcement:
    def _make_repo(self, user_id) -> tuple[MagicMock, Account, Account]:
        account_repo = MagicMock()
        src = _make_account(user_id)
        dst = _make_account(user_id)

        def get_by_id(account_id):
            if account_id == src.id:
                return src
            if account_id == dst.id:
                return dst
            return None

        account_repo.get_by_id.side_effect = get_by_id
        return account_repo, src, dst

    def test_raises_if_source_account_belongs_to_another_user(self) -> None:
        owner_id = uuid4()
        account_repo, src, dst = self._make_repo(owner_id)
        tx_repo = MagicMock()
        uc = RegisterCurrencyExchangeUseCase(account_repo=account_repo, transaction_repo=tx_repo)

        with pytest.raises(AccountAccessForbiddenError):
            uc.execute(
                RegisterCurrencyExchangeCommand(
                    user_id=uuid4(),  # different user
                    source_account_id=src.id,
                    dest_account_id=dst.id,
                    amount_out=Decimal("100"),
                    currency_out=Currency.USD,
                    amount_in=Decimal("3600"),
                    currency_in=Currency.USD,
                    exchange_rate=Decimal("36"),
                    date=date(2026, 5, 1),
                )
            )
