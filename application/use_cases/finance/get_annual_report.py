from decimal import Decimal
from uuid import UUID

from application.dtos.finance import AnnualReportResponse, AnnualReportMonthItem
from domain.repositories.finance import SavingsDepositRepository, TransactionRepository


class GetAnnualReportUseCase:
    """Full-year report: monthly breakdown + peak months + dominant expense category."""

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        savings_deposit_repo: SavingsDepositRepository,
    ) -> None:
        self._tx_repo = transaction_repo
        self._savings_repo = savings_deposit_repo

    def execute(self, user_id: UUID, year: int) -> AnnualReportResponse:
        monthly_items = []
        for m in range(1, 13):
            income_usd, expenses_usd = self._tx_repo.get_monthly_totals_usd(user_id, year, m)
            savings_usd = self._savings_repo.get_monthly_savings_usd(user_id, year, m)
            monthly_items.append(
                AnnualReportMonthItem(
                    month=m,
                    income_usd=income_usd,
                    expenses_usd=expenses_usd,
                    savings_usd=savings_usd,
                    balance_usd=income_usd - expenses_usd,
                )
            )

        total_income = sum(i.income_usd for i in monthly_items)
        total_expenses = sum(i.expenses_usd for i in monthly_items)
        total_savings = sum(i.savings_usd for i in monthly_items)

        peak_expense_month = max(monthly_items, key=lambda x: x.expenses_usd, default=None)
        peak_savings_month = max(monthly_items, key=lambda x: x.savings_usd, default=None)

        # Quarterly dominant category (simplified: Q1=1-3, Q2=4-6, Q3=7-9, Q4=10-12)
        quarterly_categories: dict[str, str | None] = {}
        for q, months_range in enumerate([(1, 3), (4, 6), (7, 9), (10, 12)], start=1):
            cat_totals: dict = {}
            for m in range(months_range[0], months_range[1] + 1):
                breakdown = self._tx_repo.get_expenses_by_category_usd(user_id, year, m)
                for cat_id, amt in breakdown.items():
                    key = str(cat_id) if cat_id else "uncategorised"
                    cat_totals[key] = cat_totals.get(key, Decimal("0")) + amt
            dominant = max(cat_totals, key=lambda k: cat_totals[k]) if cat_totals else None
            quarterly_categories[f"Q{q}"] = dominant

        return AnnualReportResponse(
            year=year,
            months=monthly_items,
            total_income_usd=total_income,
            total_expenses_usd=total_expenses,
            total_savings_usd=total_savings,
            peak_expense_month=peak_expense_month.month if peak_expense_month else None,
            peak_savings_month=peak_savings_month.month if peak_savings_month else None,
            dominant_category_by_quarter=quarterly_categories,
        )
