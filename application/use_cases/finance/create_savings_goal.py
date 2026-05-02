from application.dtos.finance import CreateSavingsGoalCommand, SavingsGoalCreatedResponse
from domain.entities.finance import SavingsGoal
from domain.repositories.finance import SavingsGoalRepository


class CreateSavingsGoalUseCase:
    def __init__(self, savings_goal_repo: SavingsGoalRepository) -> None:
        self._repo = savings_goal_repo

    def execute(self, command: CreateSavingsGoalCommand) -> SavingsGoalCreatedResponse:
        goal = SavingsGoal(
            user_id=command.user_id,
            motive=command.motive,
            target_amount_usd=command.target_amount_usd,
        )
        self._repo.save(goal)
        return SavingsGoalCreatedResponse(
            goal_id=goal.id,
            user_id=goal.user_id,
            motive=goal.motive,
            target_amount_usd=goal.target_amount_usd,
            is_completed=goal.is_completed,
        )
