import calendar
from datetime import date
from decimal import Decimal
from uuid import UUID

from application.dtos.finance import CashflowCalendarResponse, CashflowDayItem
from domain.entities.finance import TransactionType
from domain.repositories.finance import TransactionRepository


class GetCashflowCalendarUseCase:
    """For each day of the month: sum of incomes, expenses, and daily balance."""

    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self._repo = transaction_repo

    def execute(self, user_id: UUID, year: int, month: int) -> CashflowCalendarResponse:
        transactions = self._repo.list_by_user(user_id, year=year, month=month, limit=10000)

        days_in_month = calendar.monthrange(year, month)[1]
        daily: dict[int, dict] = {
            d: {"income": Decimal("0"), "expenses": Decimal("0")}
            for d in range(1, days_in_month + 1)
        }

        for tx in transactions:
            day = tx.date.day
            if tx.type == TransactionType.INCOME:
                daily[day]["income"] += tx.amount / (tx.exchange_rate or Decimal("1"))
            elif tx.type == TransactionType.EXPENSE:
                daily[day]["expenses"] += tx.amount / (tx.exchange_rate or Decimal("1"))

        items = [
            CashflowDayItem(
                day=d,
                date=date(year, month, d),
                income_usd=daily[d]["income"].quantize(Decimal("0.01")),
                expenses_usd=daily[d]["expenses"].quantize(Decimal("0.01")),
                balance_usd=(daily[d]["income"] - daily[d]["expenses"]).quantize(Decimal("0.01")),
            )
            for d in range(1, days_in_month + 1)
        ]

        return CashflowCalendarResponse(year=year, month=month, days=items)
