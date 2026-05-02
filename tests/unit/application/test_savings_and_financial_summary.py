"""
Tests for:
  - SavingsGoal and SavingsDeposit domain entities
  - CreateSavingsGoalUseCase
  - DepositToSavingsUseCase (validates USD/USDT constraint + creates SAVINGS transaction)
  - Enhanced GetMonthlyFinancialSummaryUseCase (USD-normalised totals + savings)
"""
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import (
    CreateSavingsGoalCommand,
    DepositToSavingsCommand,
    GetMonthlyFinancialSummaryQuery,
    MonthlyFinancialSummaryResponse,
    SavingsDepositCreatedResponse,
    SavingsGoalCreatedResponse,
)
from application.use_cases.finance.create_savings_goal import CreateSavingsGoalUseCase
from application.use_cases.finance.deposit_to_savings import DepositToSavingsUseCase
from application.use_cases.finance.get_monthly_financial_summary import (
    GetMonthlyFinancialSummaryUseCase,
)
from domain.entities.finance import (
    Account,
    AccountType,
    Currency,
    SavingsDeposit,
    SavingsGoal,
    TransactionType,
)
from domain.exceptions.finance import SavingsDepositCurrencyError, SavingsGoalNotFoundError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _account(user_id, currencies):
    return Account(
        user_id=user_id,
        name="Test Account",
        type=AccountType.WALLET,
        supported_currencies=currencies,
        default_currencies=currencies,
    )


def _goal(user_id):
    return SavingsGoal(
        user_id=user_id,
        motive="Emergency fund",
        target_amount_usd=Decimal("1000"),
    )


# ---------------------------------------------------------------------------
# Domain entity: SavingsGoal
# ---------------------------------------------------------------------------


class TestSavingsGoalEntity:
    def test_creates_with_correct_fields(self):
        user_id = uuid4()
        goal = SavingsGoal(
            user_id=user_id,
            motive="Vacation",
            target_amount_usd=Decimal("1500"),
        )
        assert goal.user_id == user_id
        assert goal.motive == "Vacation"
        assert goal.target_amount_usd == Decimal("1500")
        assert goal.is_completed is False

    def test_is_immutable(self):
        goal = SavingsGoal(user_id=uuid4(), motive="X", target_amount_usd=Decimal("100"))
        with pytest.raises(Exception):
            goal.motive = "Y"  # type: ignore[misc]

    def test_can_mark_completed_via_model_copy(self):
        goal = SavingsGoal(user_id=uuid4(), motive="X", target_amount_usd=Decimal("100"))
        completed = goal.model_copy(update={"is_completed": True})
        assert completed.is_completed is True
        assert goal.is_completed is False


# ---------------------------------------------------------------------------
# Domain entity: SavingsDeposit
# ---------------------------------------------------------------------------


class TestSavingsDepositEntity:
    def test_creates_valid_usd_deposit(self):
        deposit = SavingsDeposit(
            user_id=uuid4(),
            goal_id=uuid4(),
            account_id=uuid4(),
            amount=Decimal("200"),
            currency=Currency.USD,
            date=date(2026, 5, 1),
        )
        assert deposit.amount == Decimal("200")
        assert deposit.currency == Currency.USD

    def test_creates_valid_usdt_deposit(self):
        deposit = SavingsDeposit(
            user_id=uuid4(),
            goal_id=uuid4(),
            account_id=uuid4(),
            amount=Decimal("50"),
            currency=Currency.USDT,
            date=date(2026, 5, 1),
        )
        assert deposit.currency == Currency.USDT


# ---------------------------------------------------------------------------
# CreateSavingsGoalUseCase
# ---------------------------------------------------------------------------


class TestCreateSavingsGoalUseCase:
    def test_happy_path_saves_goal_and_returns_response(self):
        repo = MagicMock()
        uc = CreateSavingsGoalUseCase(savings_goal_repo=repo)
        user_id = uuid4()

        result = uc.execute(
            CreateSavingsGoalCommand(
                user_id=user_id,
                motive="Buy a car",
                target_amount_usd=Decimal("5000"),
            )
        )

        assert isinstance(result, SavingsGoalCreatedResponse)
        assert result.motive == "Buy a car"
        assert result.target_amount_usd == Decimal("5000")
        assert result.is_completed is False
        repo.save.assert_called_once()
        saved_goal = repo.save.call_args[0][0]
        assert saved_goal.user_id == user_id

    def test_goal_id_is_populated_in_response(self):
        repo = MagicMock()
        uc = CreateSavingsGoalUseCase(savings_goal_repo=repo)
        result = uc.execute(
            CreateSavingsGoalCommand(
                user_id=uuid4(), motive="Laptop", target_amount_usd=Decimal("1200")
            )
        )
        assert result.goal_id is not None


# ---------------------------------------------------------------------------
# DepositToSavingsUseCase
# ---------------------------------------------------------------------------


def _make_deposit_uc(account_currencies):
    goal_repo = MagicMock()
    deposit_repo = MagicMock()
    tx_repo = MagicMock()
    account_repo = MagicMock()

    user_id = uuid4()
    account = _account(user_id, account_currencies)
    goal = _goal(user_id)

    goal_repo.get_by_id.return_value = goal
    account_repo.get_by_id.return_value = account

    uc = DepositToSavingsUseCase(
        savings_goal_repo=goal_repo,
        savings_deposit_repo=deposit_repo,
        transaction_repo=tx_repo,
        account_repo=account_repo,
    )
    return uc, user_id, goal.id, account.id, deposit_repo, tx_repo


class TestDepositToSavingsUseCase:
    def test_usd_account_creates_deposit_and_savings_transaction(self):
        uc, user_id, goal_id, account_id, deposit_repo, tx_repo = _make_deposit_uc(
            [Currency.USD]
        )

        result = uc.execute(
            DepositToSavingsCommand(
                user_id=user_id,
                goal_id=goal_id,
                account_id=account_id,
                amount=Decimal("300"),
                currency=Currency.USD,
                date=date(2026, 5, 1),
            )
        )

        assert isinstance(result, SavingsDepositCreatedResponse)
        assert result.amount == Decimal("300")
        deposit_repo.save.assert_called_once()
        tx_repo.save.assert_called_once()
        saved_tx = tx_repo.save.call_args[0][0]
        assert saved_tx.type == TransactionType.SAVINGS
        assert saved_tx.amount == Decimal("300")
        assert saved_tx.currency == Currency.USD

    def test_usdt_account_is_accepted(self):
        uc, user_id, goal_id, account_id, deposit_repo, tx_repo = _make_deposit_uc(
            [Currency.USDT]
        )

        result = uc.execute(
            DepositToSavingsCommand(
                user_id=user_id,
                goal_id=goal_id,
                account_id=account_id,
                amount=Decimal("100"),
                currency=Currency.USDT,
                date=date(2026, 5, 1),
            )
        )

        assert isinstance(result, SavingsDepositCreatedResponse)
        deposit_repo.save.assert_called_once()

    def test_ves_account_raises_savings_deposit_currency_error(self):
        uc, user_id, goal_id, account_id, deposit_repo, tx_repo = _make_deposit_uc(
            [Currency.VES]
        )

        with pytest.raises(SavingsDepositCurrencyError):
            uc.execute(
                DepositToSavingsCommand(
                    user_id=user_id,
                    goal_id=goal_id,
                    account_id=account_id,
                    amount=Decimal("3600"),
                    currency=Currency.VES,
                    date=date(2026, 5, 1),
                )
            )

        deposit_repo.save.assert_not_called()
        tx_repo.save.assert_not_called()

    def test_goal_not_found_raises_error(self):
        goal_repo = MagicMock()
        deposit_repo = MagicMock()
        tx_repo = MagicMock()
        account_repo = MagicMock()
        goal_repo.get_by_id.return_value = None

        uc = DepositToSavingsUseCase(
            savings_goal_repo=goal_repo,
            savings_deposit_repo=deposit_repo,
            transaction_repo=tx_repo,
            account_repo=account_repo,
        )
        user_id = uuid4()

        with pytest.raises(SavingsGoalNotFoundError):
            uc.execute(
                DepositToSavingsCommand(
                    user_id=user_id,
                    goal_id=uuid4(),
                    account_id=uuid4(),
                    amount=Decimal("100"),
                    currency=Currency.USD,
                    date=date(2026, 5, 1),
                )
            )

        deposit_repo.save.assert_not_called()


# ---------------------------------------------------------------------------
# Enhanced GetMonthlyFinancialSummaryUseCase
# ---------------------------------------------------------------------------


class TestEnhancedMonthlyFinancialSummary:
    def test_returns_usd_normalised_totals_including_savings(self):
        """
        income:   $400 (base salary, from VES 14400 at rate 36 = $400)
        expenses: $300 (200 USD direct + VES 3600 at rate 36 = $100)
        savings:  $50  (USD deposit)
        balance:  $400 - $300 - $50 = $50
        budget:   $500 (fixed default)
        """
        tx_repo = MagicMock()
        savings_repo = MagicMock()
        tx_repo.get_monthly_totals_usd.return_value = (Decimal("400"), Decimal("300"))
        savings_repo.get_monthly_savings_usd.return_value = Decimal("50")

        uc = GetMonthlyFinancialSummaryUseCase(
            transaction_repo=tx_repo,
            savings_deposit_repo=savings_repo,
        )

        result = uc.execute(
            GetMonthlyFinancialSummaryQuery(user_id=uuid4(), year=2026, month=5)
        )

        assert isinstance(result, MonthlyFinancialSummaryResponse)
        assert result.total_income_usd == Decimal("400")
        assert result.total_expenses_usd == Decimal("300")
        assert result.total_savings_usd == Decimal("50")
        assert result.budget_usd == Decimal("500")
        assert result.balance_usd == Decimal("50")

    def test_returns_zeros_when_no_activity(self):
        tx_repo = MagicMock()
        savings_repo = MagicMock()
        tx_repo.get_monthly_totals_usd.return_value = (Decimal("0"), Decimal("0"))
        savings_repo.get_monthly_savings_usd.return_value = Decimal("0")

        uc = GetMonthlyFinancialSummaryUseCase(
            transaction_repo=tx_repo,
            savings_deposit_repo=savings_repo,
        )

        result = uc.execute(
            GetMonthlyFinancialSummaryQuery(user_id=uuid4(), year=2026, month=5)
        )

        assert result.total_income_usd == Decimal("0")
        assert result.total_expenses_usd == Decimal("0")
        assert result.total_savings_usd == Decimal("0")
        assert result.balance_usd == Decimal("0")

    def test_calls_repos_with_correct_user_and_period(self):
        tx_repo = MagicMock()
        savings_repo = MagicMock()
        tx_repo.get_monthly_totals_usd.return_value = (Decimal("0"), Decimal("0"))
        savings_repo.get_monthly_savings_usd.return_value = Decimal("0")

        uc = GetMonthlyFinancialSummaryUseCase(
            transaction_repo=tx_repo, savings_deposit_repo=savings_repo
        )
        user_id = uuid4()
        uc.execute(GetMonthlyFinancialSummaryQuery(user_id=user_id, year=2026, month=3))

        tx_repo.get_monthly_totals_usd.assert_called_once_with(user_id, 2026, 3)
        savings_repo.get_monthly_savings_usd.assert_called_once_with(user_id, 2026, 3)
