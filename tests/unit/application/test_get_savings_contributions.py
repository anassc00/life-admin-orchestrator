"""
Tests for:
  - GetSavingsGoalContributionsUseCase (F4: user ownership check)
  - GetSavingsGoalsUseCase             (F3: USD-only deposit filter)
"""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import SavingsDepositContributionResponse
from application.use_cases.finance.get_savings_goal_contributions import (
    GetSavingsGoalContributionsUseCase,
)
from application.use_cases.finance.get_savings_goals import GetSavingsGoalsUseCase
from domain.entities.finance import Currency, SavingsDeposit, SavingsGoal
from domain.exceptions.finance import AccountAccessForbiddenError, SavingsGoalNotFoundError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _goal(user_id, goal_id=None):
    return SavingsGoal(
        user_id=user_id,
        motive="Emergency fund",
        target_amount_usd=Decimal("1000"),
    )


def _deposit(
    user_id, goal_id, amount=Decimal("100"), currency=Currency.USD, date_val=date(2026, 5, 1)
):
    return SavingsDeposit(
        user_id=user_id,
        goal_id=goal_id,
        account_id=uuid4(),
        amount=amount,
        currency=currency,
        date=date_val,
    )


# ---------------------------------------------------------------------------
# GetSavingsGoalContributionsUseCase
# ---------------------------------------------------------------------------


class TestGetSavingsGoalContributionsUseCase:
    def test_happy_path_returns_contributions_list(self):
        goal_repo = MagicMock()
        deposit_repo = MagicMock()

        user_id = uuid4()
        goal_id = uuid4()
        goal_repo.get_by_id.return_value = _goal(user_id)
        deposit_repo.list_by_goal.return_value = [
            _deposit(user_id, goal_id, amount=Decimal("100"), date_val=date(2026, 5, 1)),
            _deposit(user_id, goal_id, amount=Decimal("200"), date_val=date(2026, 5, 15)),
        ]

        uc = GetSavingsGoalContributionsUseCase(
            savings_goal_repo=goal_repo,
            savings_deposit_repo=deposit_repo,
        )

        result = uc.execute(goal_id, user_id)

        assert len(result) == 2
        assert all(isinstance(r, SavingsDepositContributionResponse) for r in result)
        assert result[0].amount == Decimal("100")
        assert result[1].amount == Decimal("200")

    def test_returns_empty_list_when_no_deposits(self):
        goal_repo = MagicMock()
        deposit_repo = MagicMock()

        user_id = uuid4()
        goal_id = uuid4()
        goal_repo.get_by_id.return_value = _goal(user_id)
        deposit_repo.list_by_goal.return_value = []

        uc = GetSavingsGoalContributionsUseCase(
            savings_goal_repo=goal_repo,
            savings_deposit_repo=deposit_repo,
        )

        result = uc.execute(goal_id, user_id)

        assert result == []

    def test_goal_not_found_raises_error(self):
        goal_repo = MagicMock()
        deposit_repo = MagicMock()

        goal_repo.get_by_id.return_value = None

        uc = GetSavingsGoalContributionsUseCase(
            savings_goal_repo=goal_repo,
            savings_deposit_repo=deposit_repo,
        )

        with pytest.raises(SavingsGoalNotFoundError):
            uc.execute(uuid4(), uuid4())

    def test_contributions_include_notes_as_none_when_not_present(self):
        goal_repo = MagicMock()
        deposit_repo = MagicMock()

        user_id = uuid4()
        goal_id = uuid4()
        goal_repo.get_by_id.return_value = _goal(user_id)
        deposit_repo.list_by_goal.return_value = [
            _deposit(user_id, goal_id),
        ]

        uc = GetSavingsGoalContributionsUseCase(
            savings_goal_repo=goal_repo,
            savings_deposit_repo=deposit_repo,
        )

        result = uc.execute(goal_id, user_id)
        assert len(result) == 1

    # --- F4: ownership check ---

    def test_raises_forbidden_when_goal_belongs_to_different_user(self):
        goal_repo = MagicMock()
        deposit_repo = MagicMock()

        owner_id = uuid4()
        requester_id = uuid4()  # different user
        goal_id = uuid4()
        # Goal owned by owner_id
        goal_repo.get_by_id.return_value = SavingsGoal(
            id=goal_id,
            user_id=owner_id,
            motive="Emergency fund",
            target_amount_usd=Decimal("1000"),
        )

        uc = GetSavingsGoalContributionsUseCase(
            savings_goal_repo=goal_repo,
            savings_deposit_repo=deposit_repo,
        )

        with pytest.raises(AccountAccessForbiddenError):
            uc.execute(goal_id, requester_id)

        deposit_repo.list_by_goal.assert_not_called()

    def test_owner_can_access_their_own_contributions(self):
        goal_repo = MagicMock()
        deposit_repo = MagicMock()

        user_id = uuid4()
        goal_id = uuid4()
        goal_repo.get_by_id.return_value = SavingsGoal(
            id=goal_id,
            user_id=user_id,
            motive="Vacation",
            target_amount_usd=Decimal("500"),
        )
        deposit_repo.list_by_goal.return_value = []

        uc = GetSavingsGoalContributionsUseCase(
            savings_goal_repo=goal_repo,
            savings_deposit_repo=deposit_repo,
        )

        result = uc.execute(goal_id, user_id)
        assert result == []
        deposit_repo.list_by_goal.assert_called_once_with(goal_id)


# ---------------------------------------------------------------------------
# F3: GetSavingsGoalsUseCase — USD-only deposit filter
# ---------------------------------------------------------------------------


class TestGetSavingsGoalsUseCaseUsdFilter:
    def _make_uc(self, goals, deposits_by_goal):
        goal_repo = MagicMock()
        deposit_repo = MagicMock()
        goal_repo.list_by_user.return_value = goals
        deposit_repo.list_by_goal.side_effect = lambda gid: deposits_by_goal.get(gid, [])
        return GetSavingsGoalsUseCase(
            savings_goal_repo=goal_repo,
            savings_deposit_repo=deposit_repo,
        )

    def test_counts_only_usd_deposits(self):
        user_id = uuid4()
        goal = SavingsGoal(
            user_id=user_id,
            motive="Car",
            target_amount_usd=Decimal("5000"),
        )
        usd_deposit = SavingsDeposit(
            user_id=user_id,
            goal_id=goal.id,
            account_id=uuid4(),
            amount=Decimal("200"),
            currency=Currency.USD,
            date=date(2026, 5, 1),
        )
        usdt_deposit = SavingsDeposit(
            user_id=user_id,
            goal_id=goal.id,
            account_id=uuid4(),
            amount=Decimal("100"),
            currency=Currency.USDT,  # should NOT be counted
            date=date(2026, 5, 5),
        )

        uc = self._make_uc([goal], {goal.id: [usd_deposit, usdt_deposit]})
        result = uc.execute(
            __import__("application.dtos.finance", fromlist=["GetSavingsGoalsQuery"]).GetSavingsGoalsQuery(user_id=user_id)
        )

        assert len(result) == 1
        assert result[0].deposited_usd == Decimal("200")  # USDT excluded

    def test_deposited_usd_is_zero_when_only_usdt_deposits(self):
        user_id = uuid4()
        goal = SavingsGoal(
            user_id=user_id,
            motive="Laptop",
            target_amount_usd=Decimal("1200"),
        )
        usdt_deposit = SavingsDeposit(
            user_id=user_id,
            goal_id=goal.id,
            account_id=uuid4(),
            amount=Decimal("300"),
            currency=Currency.USDT,
            date=date(2026, 5, 1),
        )

        uc = self._make_uc([goal], {goal.id: [usdt_deposit]})
        from application.dtos.finance import GetSavingsGoalsQuery
        result = uc.execute(GetSavingsGoalsQuery(user_id=user_id))

        assert result[0].deposited_usd == Decimal("0")

    def test_multiple_usd_deposits_are_summed(self):
        user_id = uuid4()
        goal = SavingsGoal(
            user_id=user_id,
            motive="Emergency",
            target_amount_usd=Decimal("1000"),
        )
        deposits = [
            SavingsDeposit(
                user_id=user_id,
                goal_id=goal.id,
                account_id=uuid4(),
                amount=Decimal(str(amt)),
                currency=Currency.USD,
                date=date(2026, 5, 1),
            )
            for amt in [100, 150, 250]
        ]

        uc = self._make_uc([goal], {goal.id: deposits})
        from application.dtos.finance import GetSavingsGoalsQuery
        result = uc.execute(GetSavingsGoalsQuery(user_id=user_id))

        assert result[0].deposited_usd == Decimal("500")
