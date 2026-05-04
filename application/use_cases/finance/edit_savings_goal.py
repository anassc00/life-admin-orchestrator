from decimal import Decimal
from uuid import UUID

from application.dtos.finance import EditSavingsGoalCommand, SavingsGoalSummaryResponse
from domain.entities.finance import Currency, SavingsGoal
from domain.repositories.finance import SavingsDepositRepository, SavingsGoalRepository
from domain.exceptions.finance import SavingsGoalNotFoundError


class EditSavingsGoalUseCase:
    def __init__(
        self,
        savings_goal_repo: SavingsGoalRepository,
        savings_deposit_repo: SavingsDepositRepository,
    ) -> None:
        self._goal_repo = savings_goal_repo
        self._deposit_repo = savings_deposit_repo

    def execute(self, command: EditSavingsGoalCommand) -> SavingsGoalSummaryResponse:
        goal = self._goal_repo.get_by_id(command.goal_id)
        if not goal:
            raise SavingsGoalNotFoundError(command.goal_id)

        # Build update dict with only provided fields
        updates: dict[str, object] = {}
        if command.motive is not None:
            updates["motive"] = command.motive
        if command.target_amount_usd is not None:
            updates["target_amount_usd"] = command.target_amount_usd
        if command.expected_monthly_contribution is not None:
            updates["expected_monthly_contribution"] = command.expected_monthly_contribution

        updated_goal = goal.model_copy(update=updates)
        self._goal_repo.save(updated_goal)

        # Get deposited amount for summary
        deposited_usd = self._calculate_deposited_usd(updated_goal.id)

        return SavingsGoalSummaryResponse(
            goal_id=updated_goal.id,
            motive=updated_goal.motive,
            target_amount_usd=updated_goal.target_amount_usd,
            deposited_usd=deposited_usd,
            expected_monthly_contribution=updated_goal.expected_monthly_contribution,
            is_completed=updated_goal.is_completed,
        )

    def _calculate_deposited_usd(self, goal_id: UUID) -> Decimal:
        """Calculate total deposited amount in USD for a goal."""
        deposits = self._deposit_repo.list_by_goal(goal_id)
        return sum((d.amount for d in deposits if d.currency == Currency.USD), Decimal("0"))
