from decimal import Decimal
from uuid import UUID

from application.dtos.finance import FinanceTrendResponse, FinanceTrendMonthItem
from domain.repositories.finance import TransactionRepository


class GetFinanceTrendUseCase:
    """Return the last N months of income/expenses/savings for trend charts."""

    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self._repo = transaction_repo

    def execute(self, user_id: UUID, months: int = 6) -> FinanceTrendResponse:
        series = self._repo.get_monthly_series(user_id, months)
        items = [
            FinanceTrendMonthItem(
                year=s["year"],
                month=s["month"],
                income_usd=s["income_usd"],
                expenses_usd=s["expenses_usd"],
                savings_usd=s["savings_usd"],
                balance_usd=s["income_usd"] - s["expenses_usd"],
            )
            for s in series
        ]
        return FinanceTrendResponse(months=items)
