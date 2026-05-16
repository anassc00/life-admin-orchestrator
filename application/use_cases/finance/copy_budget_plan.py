from application.dtos.finance import BudgetPlanCreatedResponse, CopyBudgetPlanCommand
from domain.entities.finance import PlannedItem
from domain.exceptions.finance import (
    BudgetPlanAccessForbiddenError,
    BudgetPlanNotFoundError,
    NoPreviousBudgetPlanError,
)
from domain.repositories.finance import BudgetPlanRepository


class CopyBudgetPlanUseCase:
    """Copy planned items from the previous month into the target plan."""

    def __init__(self, budget_plan_repo: BudgetPlanRepository) -> None:
        self._repo = budget_plan_repo

    def execute(self, cmd: CopyBudgetPlanCommand) -> BudgetPlanCreatedResponse:
        target_plan = self._repo.get_by_id(cmd.plan_id)
        if target_plan is None:
            raise BudgetPlanNotFoundError()
        if target_plan.user_id != cmd.user_id:
            raise BudgetPlanAccessForbiddenError()

        # Find previous month
        if target_plan.month == 1:
            prev_year, prev_month = target_plan.year - 1, 12
        else:
            prev_year, prev_month = target_plan.year, target_plan.month - 1

        prev_plan = self._repo.get_by_user_and_period(cmd.user_id, prev_year, prev_month)
        if prev_plan is None:
            raise NoPreviousBudgetPlanError(target_plan.year, target_plan.month)

        prev_items = self._repo.list_planned_items(prev_plan.id)
        if not prev_items:
            return BudgetPlanCreatedResponse(
                plan_id=target_plan.id,
                user_id=target_plan.user_id,
                year=target_plan.year,
                month=target_plan.month,
                budget_usd=target_plan.budget_usd,
                income_usd=target_plan.income_usd,
            )

        # Create new PlannedItems linked to target plan (skip categories already present)
        existing_categories = {
            i.category_id for i in self._repo.list_planned_items(target_plan.id)
        }
        new_items = []
        for prev_item in prev_items:
            if prev_item.category_id not in existing_categories:
                new_items.append(
                    PlannedItem(
                        plan_id=target_plan.id,
                        category_id=prev_item.category_id,
                        planned_amount_usd=prev_item.planned_amount_usd,
                    )
                )
        if new_items:
            self._repo.save_planned_items(new_items)

        return BudgetPlanCreatedResponse(
            plan_id=target_plan.id,
            user_id=target_plan.user_id,
            year=target_plan.year,
            month=target_plan.month,
            budget_usd=target_plan.budget_usd,
            income_usd=target_plan.income_usd,
        )
