from uuid import UUID

from application.dtos.finance import SavingsDepositContributionResponse
from domain.entities.finance import SavingsGoal, SavingsDeposit
from domain.repositories.finance import SavingsGoalRepository, SavingsDepositRepository
from domain.exceptions.finance import SavingsGoalNotFoundError


class GetSavingsGoalContributionsUseCase:
    def __init__(
        self,
        savings_goal_repo: SavingsGoalRepository,
        savings_deposit_repo: SavingsDepositRepository,
    ) -> None:
        self._goal_repo = savings_goal_repo
        self._deposit_repo = savings_deposit_repo

    def execute(self, goal_id: UUID, user_id: UUID) -> list[SavingsDepositContributionResponse]:
        goal = self._goal_repo.get_by_id(goal_id)
        if not goal:
            raise SavingsGoalNotFoundError(goal_id)

        deposits = self._deposit_repo.list_by_goal(goal_id)

        return [
            SavingsDepositContributionResponse(
                deposit_id=deposit.id,
                amount=deposit.amount,
                currency=deposit.currency,
                date=deposit.date,
                notes=deposit.notes,
            )
            for deposit in deposits
        ]
