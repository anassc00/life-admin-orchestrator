from decimal import Decimal

from application.dtos.finance import BudgetVsActualSummaryResponse, GetBudgetPlanQuery
from domain.exceptions.finance import BudgetPlanNotFoundError
from domain.repositories.finance import BudgetPlanRepository, TransactionRepository


class GetBudgetVsActualSummaryUseCase:
    """Lightweight summary for dashboard: total planned vs actual, % executed, over-budget categories."""

    def __init__(
        self,
        budget_plan_repo: BudgetPlanRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._plan_repo = budget_plan_repo
        self._tx_repo = transaction_repo

    def execute(self, query: GetBudgetPlanQuery) -> BudgetVsActualSummaryResponse:
        plan = self._plan_repo.get_by_user_and_period(query.user_id, query.year, query.month)
        if plan is None:
            raise BudgetPlanNotFoundError(query.year, query.month)

        items = self._plan_repo.list_planned_items(plan.id)
        actual_by_category = self._tx_repo.get_expenses_by_category_usd(
            query.user_id, query.year, query.month
        )

        total_planned = sum((i.planned_amount_usd for i in items), Decimal("0"))
        total_actual = sum(actual_by_category.values(), Decimal("0"))
        pct_executed = (
            (total_actual / total_planned * 100).quantize(Decimal("0.01"))
            if total_planned > 0
            else Decimal("0")
        )
        over_budget_count = sum(
            1
            for item in items
            if actual_by_category.get(item.category_id, Decimal("0")) > item.planned_amount_usd
        )

        return BudgetVsActualSummaryResponse(
            plan_id=plan.id,
            year=plan.year,
            month=plan.month,
            budget_usd=plan.budget_usd,
            total_planned_usd=total_planned,
            total_actual_usd=total_actual,
            pct_executed=pct_executed,
            over_budget_categories=over_budget_count,
        )
