from application.dtos.finance import PlannedItemResponse, SetPlannedItemCommand
from domain.entities.finance import PlannedItem
from domain.exceptions.finance import BudgetPlanAccessForbiddenError, BudgetPlanNotFoundError
from domain.repositories.finance import BudgetPlanRepository


class SetPlannedItemUseCase:
    """Idempotent: creates or updates the planned item for a category within a plan."""

    def __init__(self, budget_plan_repo: BudgetPlanRepository) -> None:
        self._repo = budget_plan_repo

    def execute(self, cmd: SetPlannedItemCommand) -> PlannedItemResponse:
        plan = self._repo.get_by_id(cmd.plan_id)
        if plan is None:
            raise BudgetPlanNotFoundError()
        if plan.user_id != cmd.user_id:
            raise BudgetPlanAccessForbiddenError()

        existing = self._repo.get_planned_item_by_category(cmd.plan_id, cmd.category_id)
        if existing:
            updated = existing.model_copy(update={"planned_amount_usd": cmd.planned_amount_usd})
            self._repo.save_planned_items([updated])
            item = updated
        else:
            item = PlannedItem(
                plan_id=cmd.plan_id,
                category_id=cmd.category_id,
                planned_amount_usd=cmd.planned_amount_usd,
            )
            self._repo.save_planned_items([item])

        return PlannedItemResponse(
            item_id=item.id,
            plan_id=item.plan_id,
            category_id=item.category_id,
            planned_amount_usd=item.planned_amount_usd,
        )
