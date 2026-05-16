import math
from datetime import date
from decimal import Decimal

from application.dtos.finance import GetSavingsGoalsQuery, SuggestSavingsDistributionResponse
from domain.repositories.finance import SavingsDepositRepository, SavingsGoalRepository


class SuggestSavingsDistributionUseCase:
    """Suggest how to distribute a monthly savings amount across active goals.

    Goals are sorted by urgency: closest deadline first, then by priority.
    Allocation is proportional to urgency score (higher urgency → larger share).
    """

    def __init__(
        self,
        savings_goal_repo: SavingsGoalRepository,
        savings_deposit_repo: SavingsDepositRepository,
    ) -> None:
        self._goal_repo = savings_goal_repo
        self._deposit_repo = savings_deposit_repo

    def execute(
        self, query: GetSavingsGoalsQuery, monthly_budget_usd: Decimal
    ) -> SuggestSavingsDistributionResponse:
        goals = [g for g in self._goal_repo.list_by_user(query.user_id) if not g.is_completed]
        if not goals or monthly_budget_usd <= 0:
            return SuggestSavingsDistributionResponse(
                monthly_budget_usd=monthly_budget_usd, suggestions=[]
            )

        today = date.today()
        suggestions = []
        weights = []

        for goal in goals:
            deposited = self._deposit_repo.get_total_deposited_usd(goal.id)
            remaining = max(goal.target_amount_usd - deposited, Decimal("0"))
            if remaining <= 0:
                continue

            # Urgency: higher = closer deadline or higher expected contribution
            if goal.deadline:
                total_months = (goal.deadline.year - today.year) * 12 + (
                    goal.deadline.month - today.month
                )
                months_left = max(total_months, 1)
                urgency = float(remaining) / months_left
            elif goal.expected_monthly_contribution > 0:
                urgency = float(goal.expected_monthly_contribution)
            else:
                urgency = 1.0  # equal weight if no deadline/contribution defined

            suggestions.append(
                {
                    "goal_id": goal.id,
                    "motive": goal.motive,
                    "remaining_usd": remaining,
                    "urgency": urgency,
                }
            )
            weights.append(urgency)

        if not suggestions:
            return SuggestSavingsDistributionResponse(
                monthly_budget_usd=monthly_budget_usd, suggestions=[]
            )

        total_weight = sum(weights)
        result = []
        allocated = Decimal("0")
        for i, s in enumerate(suggestions):
            if i == len(suggestions) - 1:
                # Last item gets the remainder to avoid rounding issues
                amount = monthly_budget_usd - allocated
            else:
                share = Decimal(str(s["urgency"] / total_weight))
                amount = (monthly_budget_usd * share).quantize(Decimal("0.01"))
            allocated += amount
            result.append(
                {
                    "goal_id": s["goal_id"],
                    "motive": s["motive"],
                    "suggested_usd": amount,
                    "remaining_usd": s["remaining_usd"],
                }
            )

        return SuggestSavingsDistributionResponse(
            monthly_budget_usd=monthly_budget_usd, suggestions=result
        )
