from uuid import UUID

from application.dtos.finance import DeletePlannedItemCommand
from domain.exceptions.finance import (
    BudgetPlanAccessForbiddenError,
    BudgetPlanNotFoundError,
    PlannedItemNotFoundError,
)
from domain.repositories.finance import BudgetPlanRepository


class DeletePlannedItemUseCase:
    def __init__(self, budget_plan_repo: BudgetPlanRepository) -> None:
        self._repo = budget_plan_repo

    def execute(self, cmd: DeletePlannedItemCommand) -> dict:
        plan = self._repo.get_by_id(cmd.plan_id)
        if plan is None:
            raise BudgetPlanNotFoundError()
        if plan.user_id != cmd.user_id:
            raise BudgetPlanAccessForbiddenError()

        item = self._repo.get_planned_item_by_category(cmd.plan_id, cmd.category_id)
        if item is None:
            raise PlannedItemNotFoundError()

        self._repo.delete_planned_item(item.id)
        return {"deleted": True, "item_id": item.id}
