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


class TestGetMonthlyFinancialSummaryUseCase:
    def _make_uc(self) -> tuple[GetMonthlyFinancialSummaryUseCase, MagicMock]:
        tx_repo = MagicMock()
        uc = GetMonthlyFinancialSummaryUseCase(transaction_repo=tx_repo)
        return uc, tx_repo

    def test_returns_correct_income_expenses_and_savings(self) -> None:
        uc, tx_repo = self._make_uc()
        tx_repo.get_monthly_totals.return_value = (Decimal("2500.00"), Decimal("1000.00"))

        result = uc.execute(GetMonthlyFinancialSummaryQuery(user_id=uuid4(), year=2026, month=5))

        assert isinstance(result, MonthlyFinancialSummaryResponse)
        assert result.total_income == Decimal("2500.00")
        assert result.total_expenses == Decimal("1000.00")
        assert result.savings == Decimal("1500.00")
        assert result.year == 2026
        assert result.month == 5

    def test_savings_is_income_minus_expenses(self) -> None:
        uc, tx_repo = self._make_uc()
        tx_repo.get_monthly_totals.return_value = (Decimal("3000"), Decimal("3500"))

        result = uc.execute(GetMonthlyFinancialSummaryQuery(user_id=uuid4(), year=2026, month=5))

        assert result.savings == Decimal("-500")  # negative savings is valid

    def test_returns_zeros_when_no_transactions(self) -> None:
        uc, tx_repo = self._make_uc()
        tx_repo.get_monthly_totals.return_value = (Decimal("0"), Decimal("0"))

        result = uc.execute(GetMonthlyFinancialSummaryQuery(user_id=uuid4(), year=2026, month=1))

        assert result.total_income == Decimal("0")
        assert result.total_expenses == Decimal("0")
        assert result.savings == Decimal("0")

    def test_calls_repo_with_correct_user_year_month(self) -> None:
        uc, tx_repo = self._make_uc()
        tx_repo.get_monthly_totals.return_value = (Decimal("0"), Decimal("0"))
        user_id = uuid4()

        uc.execute(GetMonthlyFinancialSummaryQuery(user_id=user_id, year=2026, month=4))

        tx_repo.get_monthly_totals.assert_called_once_with(user_id, 2026, 4)
