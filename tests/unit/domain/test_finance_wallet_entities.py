from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from domain.entities.finance import (
    Account,
    AccountType,
    Currency,
    IncomeCategory,
    Transaction,
    TransactionType,
)


class TestAccountEntity:
    def test_account_created_with_required_fields(self) -> None:
        user_id = uuid4()
        account = Account(
            user_id=user_id,
            name="Mi Billetera",
            type=AccountType.WALLET,
            supported_currencies=[Currency.USD, Currency.USDT],
            default_currencies=[Currency.USD],
        )
        assert account.user_id == user_id
        assert account.name == "Mi Billetera"
        assert account.type == AccountType.WALLET
        assert Currency.USD in account.supported_currencies
        assert Currency.USD in account.default_currencies

    def test_account_is_frozen(self) -> None:
        account = Account(
            user_id=uuid4(),
            name="Test",
            type=AccountType.CASH,
            supported_currencies=[Currency.VES],
            default_currencies=[],
        )
        with pytest.raises(Exception):
            account.name = "Otro"  # type: ignore[misc]

    def test_two_accounts_get_different_ids(self) -> None:
        kwargs = dict(
            user_id=uuid4(),
            name="A",
            type=AccountType.BANK,
            supported_currencies=[Currency.USD],
            default_currencies=[Currency.USD],
        )
        assert Account(**kwargs).id != Account(**kwargs).id


class TestTransactionEntity:
    def test_income_transaction_created(self) -> None:
        user_id = uuid4()
        tx = Transaction(
            user_id=user_id,
            account_id=uuid4(),
            type=TransactionType.INCOME,
            amount=Decimal("500.00"),
            currency=Currency.USD,
            exchange_rate=Decimal("1.0"),
            category=IncomeCategory.SALARY,
            date=date(2026, 4, 27),
        )
        assert tx.amount == Decimal("500.00")
        assert tx.currency == Currency.USD
        assert tx.exchange_rate == Decimal("1.0")
        assert tx.category == IncomeCategory.SALARY
        assert tx.related_transaction_id is None

    def test_exchange_transactions_link_each_other(self) -> None:
        out_id = uuid4()
        in_id = uuid4()
        tx_out = Transaction(
            id=out_id,
            user_id=uuid4(),
            account_id=uuid4(),
            type=TransactionType.EXCHANGE_OUT,
            amount=Decimal("100"),
            currency=Currency.USD,
            exchange_rate=Decimal("36"),
            date=date(2026, 4, 27),
            related_transaction_id=in_id,
        )
        tx_in = Transaction(
            id=in_id,
            user_id=tx_out.user_id,
            account_id=uuid4(),
            type=TransactionType.EXCHANGE_IN,
            amount=Decimal("3600"),
            currency=Currency.VES,
            exchange_rate=Decimal("1") / Decimal("36"),
            date=date(2026, 4, 27),
            related_transaction_id=out_id,
        )
        assert tx_out.related_transaction_id == tx_in.id
        assert tx_in.related_transaction_id == tx_out.id

    def test_transaction_is_frozen(self) -> None:
        tx = Transaction(
            user_id=uuid4(),
            account_id=uuid4(),
            type=TransactionType.INCOME,
            amount=Decimal("100"),
            currency=Currency.USD,
            exchange_rate=Decimal("1.0"),
            date=date(2026, 4, 27),
        )
        with pytest.raises(Exception):
            tx.amount = Decimal("200")  # type: ignore[misc]
