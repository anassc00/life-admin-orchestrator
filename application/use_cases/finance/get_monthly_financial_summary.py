from decimal import Decimal

from application.dtos.finance import (
    GetMonthlyFinancialSummaryQuery,
    MonthlyFinancialSummaryResponse,
)
from domain.repositories.finance import SavingsDepositRepository, TransactionRepository

_BUDGET_USD = Decimal("500")


class GetMonthlyFinancialSummaryUseCase:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        savings_deposit_repo: SavingsDepositRepository,
    ) -> None:
        self._transaction_repo = transaction_repo
        self._savings_repo = savings_deposit_repo

    def execute(self, query: GetMonthlyFinancialSummaryQuery) -> MonthlyFinancialSummaryResponse:
        total_income_usd, total_expenses_usd = self._transaction_repo.get_monthly_totals_usd(
            query.user_id, query.year, query.month
        )
        total_savings_usd = self._savings_repo.get_monthly_savings_usd(
            query.user_id, query.year, query.month
        )
        balance_usd = total_income_usd - total_expenses_usd
        return MonthlyFinancialSummaryResponse(
            year=query.year,
            month=query.month,
            total_income_usd=total_income_usd,
            total_expenses_usd=total_expenses_usd,
            total_savings_usd=total_savings_usd,
            budget_usd=_BUDGET_USD,
            balance_usd=balance_usd,
        )
