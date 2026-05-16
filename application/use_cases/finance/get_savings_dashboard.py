from datetime import date
from decimal import Decimal

from application.dtos.finance import GetSavingsGoalsQuery, SavingsDashboardResponse, SavingsDashboardGoalItem
from domain.entities.finance import Currency
from domain.repositories.finance import SavingsDepositRepository, SavingsGoalRepository, TransactionRepository


class GetSavingsDashboardUseCase:
    """Aggregate endpoint for the savings widget: current-month summary + all goals with progress."""

    def __init__(
        self,
        savings_goal_repo: SavingsGoalRepository,
        savings_deposit_repo: SavingsDepositRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._goal_repo = savings_goal_repo
        self._deposit_repo = savings_deposit_repo
        self._tx_repo = transaction_repo

    def execute(self, query: GetSavingsGoalsQuery) -> SavingsDashboardResponse:
        today = date.today()
        year, month = today.year, today.month

        # Monthly totals
        saved_this_month = self._deposit_repo.get_monthly_savings_usd(query.user_id, year, month)
        income_usd, _ = self._tx_repo.get_monthly_totals_usd(query.user_id, year, month)
        savings_rate_pct = (
            (saved_this_month / income_usd * 100).quantize(Decimal("0.01"))
            if income_usd > 0
            else Decimal("0")
        )

        # Per-goal breakdown for the month
        monthly_by_goal = dict(
            self._deposit_repo.get_monthly_deposits_by_goal(query.user_id, year, month)
        )

        goals = self._goal_repo.list_by_user(query.user_id)
        goal_items = []
        for goal in goals:
            deposited_usd = self._deposit_repo.get_total_deposited_usd(goal.id)
            progress_pct = (
                (deposited_usd / goal.target_amount_usd * 100).quantize(Decimal("0.01"))
                if goal.target_amount_usd > 0
                else Decimal("0")
            )
            goal_items.append(
                SavingsDashboardGoalItem(
                    goal_id=goal.id,
                    motive=goal.motive,
                    target_amount_usd=goal.target_amount_usd,
                    deposited_usd=deposited_usd,
                    deposited_this_month_usd=monthly_by_goal.get(goal.id, Decimal("0")),
                    progress_pct=min(progress_pct, Decimal("100")),
                    is_completed=goal.is_completed,
                    deadline=goal.deadline,
                    priority=goal.priority,
                )
            )

        active_count = sum(1 for g in goals if not g.is_completed)
        completed_count = sum(1 for g in goals if g.is_completed)

        return SavingsDashboardResponse(
            year=year,
            month=month,
            saved_this_month_usd=saved_this_month,
            savings_rate_pct=savings_rate_pct,
            active_goals_count=active_count,
            completed_goals_count=completed_count,
            goals=goal_items,
        )
