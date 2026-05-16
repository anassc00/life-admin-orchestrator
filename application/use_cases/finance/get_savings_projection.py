import math
from datetime import date
from decimal import Decimal

from application.dtos.finance import GetSavingsGoalsQuery, SavingsProjectionResponse
from domain.entities.finance import Currency
from domain.repositories.finance import SavingsDepositRepository, SavingsGoalRepository


class GetSavingsProjectionUseCase:
    """For each active savings goal, calculate remaining_usd and months_to_completion."""

    def __init__(
        self,
        savings_goal_repo: SavingsGoalRepository,
        savings_deposit_repo: SavingsDepositRepository,
    ) -> None:
        self._goal_repo = savings_goal_repo
        self._deposit_repo = savings_deposit_repo

    def execute(self, query: GetSavingsGoalsQuery) -> list[SavingsProjectionResponse]:
        goals = self._goal_repo.list_by_user(query.user_id)
        today = date.today()
        result = []

        for goal in goals:
            if goal.is_completed:
                continue

            deposited_usd = self._deposit_repo.get_total_deposited_usd(goal.id)
            remaining_usd = max(goal.target_amount_usd - deposited_usd, Decimal("0"))

            months_to_completion = None
            projected_completion_date = None

            if goal.expected_monthly_contribution > 0 and remaining_usd > 0:
                months = math.ceil(float(remaining_usd / goal.expected_monthly_contribution))
                months_to_completion = months
                total_months = today.year * 12 + today.month + months - 1
                proj_year = total_months // 12
                proj_month = total_months % 12 + 1
                projected_completion_date = date(proj_year, proj_month, 1)
            elif remaining_usd <= 0:
                months_to_completion = 0
                projected_completion_date = today

            result.append(
                SavingsProjectionResponse(
                    goal_id=goal.id,
                    motive=goal.motive,
                    target_amount_usd=goal.target_amount_usd,
                    deposited_usd=deposited_usd,
                    remaining_usd=remaining_usd,
                    expected_monthly_contribution=goal.expected_monthly_contribution,
                    months_to_completion=months_to_completion,
                    projected_completion_date=projected_completion_date,
                    deadline=goal.deadline,
                    priority=goal.priority,
                )
            )

        return sorted(result, key=lambda x: (x.priority, x.goal_id))
