from application.dtos.finance import CreateSavingsDistributionCommand, SavingsDistributionResponse
from domain.entities.finance import SavingsDistributionItem, SavingsDistributionPlan
from domain.exceptions.finance import SavingsGoalNotFoundError
from domain.repositories.finance import (
    SavingsDistributionRepository,
    SavingsGoalRepository,
)


class CreateMonthlySavingsDistributionUseCase:
    """Define how savings for a month should be distributed across goals."""

    def __init__(
        self,
        distribution_repo: SavingsDistributionRepository,
        savings_goal_repo: SavingsGoalRepository,
    ) -> None:
        self._distribution_repo = distribution_repo
        self._goal_repo = savings_goal_repo

    def execute(self, cmd: CreateSavingsDistributionCommand) -> SavingsDistributionResponse:
        # Validate all goals belong to the user
        for item in cmd.items:
            goal = self._goal_repo.get_by_id(item.goal_id)
            if goal is None or goal.user_id != cmd.user_id:
                raise SavingsGoalNotFoundError(item.goal_id)

        total = sum(i.planned_usd for i in cmd.items)

        # Check if plan already exists → replace it
        existing = self._distribution_repo.get_by_user_and_period(
            cmd.user_id, cmd.year, cmd.month
        )
        from uuid import uuid4
        plan_id = existing.id if existing else uuid4()

        dist_items = [
            SavingsDistributionItem(
                plan_id=plan_id,
                goal_id=item.goal_id,
                planned_usd=item.planned_usd,
            )
            for item in cmd.items
        ]
        plan = SavingsDistributionPlan(
            id=plan_id,
            user_id=cmd.user_id,
            year=cmd.year,
            month=cmd.month,
            total_planned_usd=total,
            items=dist_items,
        )
        self._distribution_repo.save(plan)

        return SavingsDistributionResponse(
            plan_id=plan.id,
            year=plan.year,
            month=plan.month,
            total_planned_usd=plan.total_planned_usd,
            items=[
                {"goal_id": i.goal_id, "planned_usd": i.planned_usd} for i in dist_items
            ],
        )
