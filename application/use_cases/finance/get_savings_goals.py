from decimal import Decimal

from application.dtos.finance import GetSavingsGoalsQuery, SavingsGoalSummaryResponse
from domain.repositories.finance import SavingsDepositRepository, SavingsGoalRepository


class GetSavingsGoalsUseCase:
    def __init__(
        self,
        savings_goal_repo: SavingsGoalRepository,
        savings_deposit_repo: SavingsDepositRepository,
    ) -> None:
        self._goal_repo = savings_goal_repo
        self._deposit_repo = savings_deposit_repo

    def execute(self, query: GetSavingsGoalsQuery) -> list[SavingsGoalSummaryResponse]:
        goals = self._goal_repo.list_by_user(query.user_id)
        result = []
        for goal in goals:
            deposits = self._deposit_repo.list_by_goal(goal.id)
            deposited_usd = sum((d.amount for d in deposits), Decimal("0"))
            result.append(
                SavingsGoalSummaryResponse(
                    goal_id=goal.id,
                    motive=goal.motive,
                    target_amount_usd=goal.target_amount_usd,
                    deposited_usd=deposited_usd,
                    is_completed=goal.is_completed,
                )
            )
        return result
