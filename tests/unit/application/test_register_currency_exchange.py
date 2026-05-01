from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import (
    CurrencyExchangeRegisteredResponse,
    RegisterCurrencyExchangeCommand,
)
from application.use_cases.finance.register_currency_exchange import RegisterCurrencyExchangeUseCase
from domain.entities.finance import Currency, TransactionType
from domain.exceptions.finance import AccountNotFoundError


class TestRegisterCurrencyExchangeUseCase:
    def _make_uc(self) -> tuple[RegisterCurrencyExchangeUseCase, MagicMock, MagicMock]:
        account_repo = MagicMock()
        tx_repo = MagicMock()

        out_account = MagicMock()
        out_account.user_id = uuid4()
        in_account = MagicMock()
        in_account.user_id = out_account.user_id

        def get_by_id(account_id):
            if account_id == _out_id:
                return out_account
            if account_id == _in_id:
                return in_account
            return None

        _out_id = uuid4()
        _in_id = uuid4()
        account_repo.get_by_id.side_effect = get_by_id
        uc = RegisterCurrencyExchangeUseCase(account_repo=account_repo, transaction_repo=tx_repo)
        return uc, account_repo, tx_repo, _out_id, _in_id, out_account.user_id

    def test_creates_linked_exchange_pair(self) -> None:
        uc, account_repo, tx_repo, out_id, in_id, user_id = self._make_uc()

        result = uc.execute(
            RegisterCurrencyExchangeCommand(
                user_id=user_id,
                source_account_id=out_id,
                dest_account_id=in_id,
                amount_out=Decimal("100"),
                currency_out=Currency.USD,
                amount_in=Decimal("3600"),
                currency_in=Currency.VES,
                exchange_rate=Decimal("36"),
                date=date(2026, 4, 27),
            )
        )

        assert isinstance(result, CurrencyExchangeRegisteredResponse)
        assert result.amount_out == Decimal("100")
        assert result.amount_in == Decimal("3600")
        assert result.currency_out == Currency.USD
        assert result.currency_in == Currency.VES
        # Both transactions must be saved atomically
        assert tx_repo.save_exchange_pair.called

    def test_exchange_pair_transactions_are_linked(self) -> None:
        uc, account_repo, tx_repo, out_id, in_id, user_id = self._make_uc()

        uc.execute(
            RegisterCurrencyExchangeCommand(
                user_id=user_id,
                source_account_id=out_id,
                dest_account_id=in_id,
                amount_out=Decimal("50"),
                currency_out=Currency.USDT,
                amount_in=Decimal("1750"),
                currency_in=Currency.VES,
                exchange_rate=Decimal("35"),
                date=date(2026, 4, 27),
            )
        )

        args = tx_repo.save_exchange_pair.call_args[0]
        tx_out, tx_in = args[0], args[1]
        assert tx_out.type == TransactionType.EXCHANGE_OUT
        assert tx_in.type == TransactionType.EXCHANGE_IN
        assert tx_out.related_transaction_id == tx_in.id
        assert tx_in.related_transaction_id == tx_out.id

    def test_raises_if_source_account_not_found(self) -> None:
        uc, account_repo, tx_repo, out_id, in_id, user_id = self._make_uc()
        account_repo.get_by_id.side_effect = lambda _: None

        with pytest.raises(AccountNotFoundError):
            uc.execute(
                RegisterCurrencyExchangeCommand(
                    user_id=user_id,
                    source_account_id=uuid4(),
                    dest_account_id=in_id,
                    amount_out=Decimal("100"),
                    currency_out=Currency.USD,
                    amount_in=Decimal("3600"),
                    currency_in=Currency.VES,
                    exchange_rate=Decimal("36"),
                    date=date(2026, 4, 27),
                )
            )
