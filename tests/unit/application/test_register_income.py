from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import IncomeRegisteredResponse, RegisterIncomeCommand
from application.use_cases.finance.register_income import RegisterIncomeUseCase
from domain.entities.finance import Currency, IncomeCategory, TransactionType
from domain.exceptions.finance import AccountNotFoundError


class TestRegisterIncomeUseCase:
    def _make_uc(self) -> tuple[RegisterIncomeUseCase, MagicMock, MagicMock]:
        account_repo = MagicMock()
        tx_repo = MagicMock()
        account = MagicMock()
        account.user_id = uuid4()
        account_repo.get_by_id.return_value = account
        uc = RegisterIncomeUseCase(account_repo=account_repo, transaction_repo=tx_repo)
        return uc, account_repo, tx_repo

    def test_registers_salary_income(self) -> None:
        uc, account_repo, tx_repo = self._make_uc()
        user_id = account_repo.get_by_id.return_value.user_id
        account_id = uuid4()

        result = uc.execute(
            RegisterIncomeCommand(
                user_id=user_id,
                account_id=account_id,
                amount=Decimal("2500.00"),
                currency=Currency.USD,
                exchange_rate=Decimal("1.0"),
                category=IncomeCategory.SALARY,
                date=date(2026, 4, 27),
            )
        )

        assert isinstance(result, IncomeRegisteredResponse)
        assert result.amount == Decimal("2500.00")
        assert result.type == TransactionType.INCOME
        tx_repo.save.assert_called_once()

    def test_raises_if_account_not_found(self) -> None:
        uc, account_repo, tx_repo = self._make_uc()
        account_repo.get_by_id.return_value = None

        with pytest.raises(AccountNotFoundError):
            uc.execute(
                RegisterIncomeCommand(
                    user_id=uuid4(),
                    account_id=uuid4(),
                    amount=Decimal("100"),
                    currency=Currency.USD,
                    exchange_rate=Decimal("1.0"),
                    category=IncomeCategory.OTHER_PAYMENTS,
                    date=date(2026, 4, 27),
                )
            )

    def test_notes_are_optional(self) -> None:
        uc, account_repo, tx_repo = self._make_uc()
        user_id = account_repo.get_by_id.return_value.user_id

        result = uc.execute(
            RegisterIncomeCommand(
                user_id=user_id,
                account_id=uuid4(),
                amount=Decimal("50"),
                currency=Currency.USDT,
                exchange_rate=Decimal("1.0"),
                category=IncomeCategory.PROFESSIONAL_FEES,
                date=date(2026, 4, 27),
            )
        )

        assert result.notes is None
