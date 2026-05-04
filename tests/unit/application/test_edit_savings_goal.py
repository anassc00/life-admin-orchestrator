"""
Tests for:
  - EditSavingsGoalUseCase
  - SavingsGoal entity with expected_monthly_contribution
"""

from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import EditSavingsGoalCommand, SavingsGoalSummaryResponse
from application.use_cases.finance.edit_savings_goal import EditSavingsGoalUseCase
from domain.entities.finance import SavingsGoal
from domain.exceptions.finance import SavingsGoalNotFoundError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _goal(user_id, goal_id=None, motive="Emergency fund", target_amount_usd=Decimal("1000"), expected_monthly_contribution=Decimal("0")):
    return SavingsGoal(
        id=goal_id if goal_id else uuid4(),
        user_id=user_id,
        motive=motive,
        target_amount_usd=target_amount_usd,
        expected_monthly_contribution=expected_monthly_contribution,
    )


# ---------------------------------------------------------------------------
# Domain entity: SavingsGoal with expected_monthly_contribution
# ---------------------------------------------------------------------------


class TestSavingsGoalEntityWithExpectedMonthlyContribution:
    def test_creates_with_expected_monthly_contribution(self):
        user_id = uuid4()
        goal = SavingsGoal(
            user_id=user_id,
            motive="Vacation",
            target_amount_usd=Decimal("1500"),
            expected_monthly_contribution=Decimal("100"),
        )
        assert goal.expected_monthly_contribution == Decimal("100")

    def test_default_expected_monthly_contribution_is_zero(self):
        user_id = uuid4()
        goal = SavingsGoal(
            user_id=user_id,
            motive="Vacation",
            target_amount_usd=Decimal("1500"),
        )
        assert goal.expected_monthly_contribution == Decimal("0")

    def test_can_update_via_model_copy(self):
        user_id = uuid4()
        goal = SavingsGoal(
            user_id=user_id,
            motive="X",
            target_amount_usd=Decimal("100"),
            expected_monthly_contribution=Decimal("10"),
        )
        updated = goal.model_copy(update={"expected_monthly_contribution": Decimal("50"), "motive": "Y"})
        assert updated.expected_monthly_contribution == Decimal("50")
        assert updated.motive == "Y"
        assert goal.expected_monthly_contribution == Decimal("10")


# ---------------------------------------------------------------------------
# EditSavingsGoalUseCase
# ---------------------------------------------------------------------------


class TestEditSavingsGoalUseCase:
    def test_happy_path_updates_goal_and_returns_response(self):
        repo = MagicMock()
        deposit_repo = MagicMock()
        user_id = uuid4()
        goal_id = uuid4()
        existing_goal = _goal(user_id, goal_id=goal_id, motive="Old", target_amount_usd=Decimal("500"))

        repo.get_by_id.return_value = existing_goal

        uc = EditSavingsGoalUseCase(savings_goal_repo=repo, savings_deposit_repo=deposit_repo)

        result = uc.execute(
            EditSavingsGoalCommand(
                user_id=user_id,
                goal_id=goal_id,
                motive="New motive",
                target_amount_usd=Decimal("1000"),
                expected_monthly_contribution=Decimal("50"),
            )
        )

        assert isinstance(result, SavingsGoalSummaryResponse)
        assert result.motive == "New motive"
        assert result.target_amount_usd == Decimal("1000")
        assert result.goal_id == goal_id
        repo.save.assert_called_once()

    def test_updates_only_provided_fields(self):
        repo = MagicMock()
        deposit_repo = MagicMock()
        user_id = uuid4()
        goal_id = uuid4()
        existing_goal = _goal(
            user_id,
            motive="Original",
            target_amount_usd=Decimal("500"),
            expected_monthly_contribution=Decimal("25"),
        )

        repo.get_by_id.return_value = existing_goal

        uc = EditSavingsGoalUseCase(savings_goal_repo=repo, savings_deposit_repo=deposit_repo)

        result = uc.execute(
            EditSavingsGoalCommand(
                user_id=user_id,
                goal_id=goal_id,
                motive="Updated",
                target_amount_usd=None,
                expected_monthly_contribution=None,
            )
        )

        assert result.motive == "Updated"
        assert result.target_amount_usd == Decimal("500")
        saved_goal = repo.save.call_args[0][0]
        assert saved_goal.target_amount_usd == Decimal("500")
        assert saved_goal.expected_monthly_contribution == Decimal("25")

    def test_goal_not_found_raises_error(self):
        repo = MagicMock()
        deposit_repo = MagicMock()
        repo.get_by_id.return_value = None

        uc = EditSavingsGoalUseCase(savings_goal_repo=repo, savings_deposit_repo=deposit_repo)
        user_id = uuid4()

        with pytest.raises(SavingsGoalNotFoundError):
            uc.execute(
                EditSavingsGoalCommand(
                    user_id=user_id,
                    goal_id=uuid4(),
                    motive="New",
                    target_amount_usd=Decimal("1000"),
                    expected_monthly_contribution=None,
                )
            )

        repo.save.assert_not_called()
