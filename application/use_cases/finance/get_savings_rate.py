from datetime import date
from decimal import Decimal

from application.dtos.finance import GetSavingsRateQuery, SavingsRateResponse, SavingsRateMonthItem
from domain.repositories.finance import SavingsDepositRepository, TransactionRepository


class GetSavingsRateUseCase:
    """Return monthly savings rate (savings_usd / income_usd * 100) for the last N months."""

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        savings_deposit_repo: SavingsDepositRepository,
    ) -> None:
        self._tx_repo = transaction_repo
        self._savings_repo = savings_deposit_repo

    def execute(self, query: GetSavingsRateQuery) -> SavingsRateResponse:
        today = date.today()
        items = []

        for i in range(query.months - 1, -1, -1):
            total_months = today.year * 12 + today.month - 1 - i
            y = total_months // 12
            m = total_months % 12 + 1

            income_usd, _ = self._tx_repo.get_monthly_totals_usd(query.user_id, y, m)
            savings_usd = self._savings_repo.get_monthly_savings_usd(query.user_id, y, m)

            rate_pct = (
                (savings_usd / income_usd * 100).quantize(Decimal("0.01"))
                if income_usd > 0
                else Decimal("0")
            )
            items.append(
                SavingsRateMonthItem(
                    year=y,
                    month=m,
                    income_usd=income_usd,
                    savings_usd=savings_usd,
                    rate_pct=rate_pct,
                )
            )

        avg_rate = (
            sum(i.rate_pct for i in items) / len(items) if items else Decimal("0")
        )
        return SavingsRateResponse(
            months=items,
            avg_rate_pct=avg_rate.quantize(Decimal("0.01")),
        )
