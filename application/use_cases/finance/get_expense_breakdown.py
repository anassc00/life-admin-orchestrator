from decimal import Decimal
from uuid import UUID

from application.dtos.finance import ExpenseBreakdownResponse, ExpenseBreakdownItem
from domain.repositories.finance import ExpenseCategoryRepository, TransactionRepository


class GetExpenseBreakdownUseCase:
    """Expense breakdown by category for a given month."""

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        category_repo: ExpenseCategoryRepository,
    ) -> None:
        self._tx_repo = transaction_repo
        self._cat_repo = category_repo

    def execute(self, user_id: UUID, year: int, month: int) -> ExpenseBreakdownResponse:
        by_category = self._tx_repo.get_expenses_by_category_usd(user_id, year, month)
        total = sum(by_category.values(), Decimal("0"))
        items = []

        for category_id, amount in sorted(by_category.items(), key=lambda x: -x[1]):
            category_name = None
            if category_id:
                cat = self._cat_repo.get_by_id(category_id)
                category_name = cat.name if cat else "Unknown"
            else:
                category_name = "Uncategorised"

            pct = (
                (amount / total * 100).quantize(Decimal("0.01")) if total > 0 else Decimal("0")
            )
            items.append(
                ExpenseBreakdownItem(
                    category_id=category_id,
                    category_name=category_name,
                    total_usd=amount,
                    pct_of_total=pct,
                )
            )

        return ExpenseBreakdownResponse(
            year=year,
            month=month,
            total_expenses_usd=total,
            items=items,
        )
