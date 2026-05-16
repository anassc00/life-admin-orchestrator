from decimal import Decimal

from application.dtos.finance import (
    BudgetPlanDetailResponse,
    BudgetPlanItemDetailResponse,
    GetBudgetPlanQuery,
)
from domain.exceptions.finance import BudgetPlanAccessForbiddenError, BudgetPlanNotFoundError
from domain.repositories.finance import (
    BudgetPlanRepository,
    ExpenseCategoryRepository,
    TransactionRepository,
)


class GetBudgetPlanUseCase:
    """Return the budget plan with planned vs actual per category and deviation."""

    def __init__(
        self,
        budget_plan_repo: BudgetPlanRepository,
        transaction_repo: TransactionRepository,
        category_repo: ExpenseCategoryRepository,
    ) -> None:
        self._plan_repo = budget_plan_repo
        self._tx_repo = transaction_repo
        self._cat_repo = category_repo

    def execute(self, query: GetBudgetPlanQuery) -> BudgetPlanDetailResponse:
        plan = self._plan_repo.get_by_user_and_period(query.user_id, query.year, query.month)
        if plan is None:
            raise BudgetPlanNotFoundError(query.year, query.month)
        if plan.user_id != query.user_id:
            raise BudgetPlanAccessForbiddenError()

        items = self._plan_repo.list_planned_items(plan.id)
        actual_by_category = self._tx_repo.get_expenses_by_category_usd(
            query.user_id, query.year, query.month
        )

        detail_items = []
        total_planned = Decimal("0")
        total_actual = Decimal("0")

        for item in items:
            actual_usd = actual_by_category.get(item.category_id, Decimal("0"))
            deviation_usd = item.planned_amount_usd - actual_usd
            deviation_pct = (
                (actual_usd / item.planned_amount_usd * 100)
                if item.planned_amount_usd > 0
                else Decimal("0")
            )
            over_budget = actual_usd > item.planned_amount_usd

            # Resolve category name
            category_name = None
            if item.category_id:
                cat = self._cat_repo.get_by_id(item.category_id)
                category_name = cat.name if cat else None

            detail_items.append(
                BudgetPlanItemDetailResponse(
                    item_id=item.id,
                    category_id=item.category_id,
                    category_name=category_name,
                    planned_usd=item.planned_amount_usd,
                    actual_usd=actual_usd,
                    deviation_usd=deviation_usd,
                    deviation_pct=deviation_pct.quantize(Decimal("0.01")),
                    over_budget=over_budget,
                )
            )
            total_planned += item.planned_amount_usd
            total_actual += actual_usd

        # 50/30/20 suggestion when income_usd is set (B8)
        rule_50_30_20 = None
        if plan.income_usd and plan.income_usd > 0:
            rule_50_30_20 = {
                "needs_usd": (plan.income_usd * Decimal("0.50")).quantize(Decimal("0.01")),
                "wants_usd": (plan.income_usd * Decimal("0.30")).quantize(Decimal("0.01")),
                "savings_usd": (plan.income_usd * Decimal("0.20")).quantize(Decimal("0.01")),
            }

        return BudgetPlanDetailResponse(
            plan_id=plan.id,
            user_id=plan.user_id,
            year=plan.year,
            month=plan.month,
            budget_usd=plan.budget_usd,
            income_usd=plan.income_usd,
            total_planned_usd=total_planned,
            total_actual_usd=total_actual,
            items=detail_items,
            rule_50_30_20=rule_50_30_20,
        )
