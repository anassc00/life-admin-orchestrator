from application.dtos.finance import (
    GetMonthlyFinancialSummaryQuery,
    MonthlyFinancialSummaryResponse,
)
from domain.repositories.finance import TransactionRepository


class GetMonthlyFinancialSummaryUseCase:
    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self._transaction_repo = transaction_repo

    def execute(self, query: GetMonthlyFinancialSummaryQuery) -> MonthlyFinancialSummaryResponse:
        total_income, total_expenses = self._transaction_repo.get_monthly_totals(
            query.user_id, query.year, query.month
        )
        return MonthlyFinancialSummaryResponse(
            year=query.year,
            month=query.month,
            total_income=total_income,
            total_expenses=total_expenses,
            savings=total_income - total_expenses,
        )
