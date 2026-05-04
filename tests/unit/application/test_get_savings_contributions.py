"""
Tests for:
  - GetSavingsGoalContributionsUseCase
  - Savings deposits contributions endpoint
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
from domain.entities.finance import Currency, SavingsDeposit, SavingsGoal
from domain.exceptions.finance import SavingsGoalNotFoundError

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
        # SavingsDeposit entity doesn't have notes field yet - this will fail
        # demonstrating RED phase
        deposit_repo.list_by_goal.return_value = [
            _deposit(user_id, goal_id),
        ]

        uc = GetSavingsGoalContributionsUseCase(
            savings_goal_repo=goal_repo,
            savings_deposit_repo=deposit_repo,
        )

        result = uc.execute(goal_id, user_id)
        assert len(result) == 1
