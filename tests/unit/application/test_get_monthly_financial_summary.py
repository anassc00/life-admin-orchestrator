from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

from application.dtos.finance import (
    GetMonthlyFinancialSummaryQuery,
    MonthlyFinancialSummaryResponse,
)
from application.use_cases.finance.get_monthly_financial_summary import (
    GetMonthlyFinancialSummaryUseCase,
)


def _make_uc():
    tx_repo = MagicMock()
    savings_repo = MagicMock()
    savings_repo.get_monthly_savings_usd.return_value = Decimal("0")
    uc = GetMonthlyFinancialSummaryUseCase(
        transaction_repo=tx_repo,
        savings_deposit_repo=savings_repo,
    )
    return uc, tx_repo, savings_repo


class TestGetMonthlyFinancialSummaryUseCase:
    def test_returns_usd_normalised_totals(self) -> None:
        uc, tx_repo, savings_repo = _make_uc()
        tx_repo.get_monthly_totals_usd.return_value = (Decimal("2500.00"), Decimal("1000.00"))

        result = uc.execute(GetMonthlyFinancialSummaryQuery(user_id=uuid4(), year=2026, month=5))

        assert isinstance(result, MonthlyFinancialSummaryResponse)
        assert result.total_income_usd == Decimal("2500.00")
        assert result.total_expenses_usd == Decimal("1000.00")
        assert result.total_savings_usd == Decimal("0")
        assert result.balance_usd == Decimal("1500.00")
        assert result.budget_usd == Decimal("500")
        assert result.year == 2026
        assert result.month == 5

    def test_balance_can_be_negative(self) -> None:
        uc, tx_repo, _ = _make_uc()
        tx_repo.get_monthly_totals_usd.return_value = (Decimal("300"), Decimal("400"))

        result = uc.execute(GetMonthlyFinancialSummaryQuery(user_id=uuid4(), year=2026, month=5))

        assert result.balance_usd == Decimal("-100")

    def test_returns_zeros_when_no_transactions(self) -> None:
        uc, tx_repo, _ = _make_uc()
        tx_repo.get_monthly_totals_usd.return_value = (Decimal("0"), Decimal("0"))

        result = uc.execute(GetMonthlyFinancialSummaryQuery(user_id=uuid4(), year=2026, month=1))

        assert result.total_income_usd == Decimal("0")
        assert result.total_expenses_usd == Decimal("0")
        assert result.balance_usd == Decimal("0")

    def test_calls_repos_with_correct_user_and_period(self) -> None:
        uc, tx_repo, savings_repo = _make_uc()
        tx_repo.get_monthly_totals_usd.return_value = (Decimal("0"), Decimal("0"))
        user_id = uuid4()

        uc.execute(GetMonthlyFinancialSummaryQuery(user_id=user_id, year=2026, month=4))

        tx_repo.get_monthly_totals_usd.assert_called_once_with(user_id, 2026, 4)
        savings_repo.get_monthly_savings_usd.assert_called_once_with(user_id, 2026, 4)
