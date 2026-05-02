"""Unit tests for CreateExpenseCategoryUseCase, GetExpenseCategoriesUseCase,
and RegisterExpenseUseCase."""

import datetime
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import (
    CreateExpenseCategoryCommand,
    ExpenseCategoryCreatedResponse,
    GetExpenseCategoriesQuery,
    RegisterExpenseCommand,
)
from application.use_cases.finance.create_expense_category import CreateExpenseCategoryUseCase
from application.use_cases.finance.get_expense_categories import GetExpenseCategoriesUseCase
from application.use_cases.finance.register_expense import RegisterExpenseUseCase
from domain.entities.finance import Account, AccountType, Currency, ExpenseCategory
from domain.exceptions.finance import (
    AccountAccessForbiddenError,
    AccountNotFoundError,
    ExpenseCategoryAlreadyExistsError,
    ExpenseCategoryNotFoundError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_account(user_id=None):
    uid = user_id or uuid4()
    return Account(
        user_id=uid,
        name="Billetera USD",
        type=AccountType.WALLET,
        supported_currencies=[Currency.USD],
        default_currencies=[Currency.USD],
    )


def _make_category(user_id=None):
    uid = user_id or uuid4()
    return ExpenseCategory(
        user_id=uid,
        name="Alimentación",
        is_fixed_expense=False,
        default_amount_usd=Decimal("200.00"),
    )


# ---------------------------------------------------------------------------
# CreateExpenseCategoryUseCase
# ---------------------------------------------------------------------------


class TestCreateExpenseCategoryUseCase:
    def _make_uc(self):
        repo = MagicMock()
        uc = CreateExpenseCategoryUseCase(category_repo=repo)
        return uc, repo

    def test_creates_category_and_returns_response(self):
        uc, repo = self._make_uc()
        repo.exists_by_name_and_user.return_value = False
        user_id = uuid4()

        result = uc.execute(
            CreateExpenseCategoryCommand(
                user_id=user_id,
                name="Alimentación",
                is_fixed_expense=False,
                default_amount_usd=Decimal("200.00"),
            )
        )

        assert isinstance(result, ExpenseCategoryCreatedResponse)
        assert result.name == "Alimentación"
        repo.save.assert_called_once()

    def test_raises_when_category_name_already_exists_for_user(self):
        uc, repo = self._make_uc()
        user_id = uuid4()
        repo.exists_by_name_and_user.return_value = True

        with pytest.raises(ExpenseCategoryAlreadyExistsError):
            uc.execute(
                CreateExpenseCategoryCommand(
                    user_id=user_id,
                    name="Duplicado",
                    is_fixed_expense=True,
                    default_amount_usd=Decimal("100.00"),
                )
            )

        repo.save.assert_not_called()


# ---------------------------------------------------------------------------
# GetExpenseCategoriesUseCase
# ---------------------------------------------------------------------------


class TestGetExpenseCategoriesUseCase:
    def _make_uc(self):
        repo = MagicMock()
        uc = GetExpenseCategoriesUseCase(category_repo=repo)
        return uc, repo

    def test_returns_list_of_categories_for_user(self):
        uc, repo = self._make_uc()
        user_id = uuid4()
        cat1 = _make_category(user_id=user_id)
        cat2 = _make_category(user_id=user_id)
        repo.list_by_user.return_value = [cat1, cat2]

        result = uc.execute(GetExpenseCategoriesQuery(user_id=user_id))

        assert len(result) == 2
        repo.list_by_user.assert_called_once_with(user_id)

    def test_returns_empty_list_when_no_categories(self):
        uc, repo = self._make_uc()
        repo.list_by_user.return_value = []

        result = uc.execute(GetExpenseCategoriesQuery(user_id=uuid4()))

        assert result == []


# ---------------------------------------------------------------------------
# RegisterExpenseUseCase
# ---------------------------------------------------------------------------


class TestRegisterExpenseUseCase:
    def _make_uc(self):
        account_repo = MagicMock()
        category_repo = MagicMock()
        transaction_repo = MagicMock()
        uc = RegisterExpenseUseCase(
            account_repo=account_repo,
            category_repo=category_repo,
            transaction_repo=transaction_repo,
        )
        return uc, account_repo, category_repo, transaction_repo

    def _command(self, user_id, account_id, category_id):
        return RegisterExpenseCommand(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            amount=Decimal("50.00"),
            currency=Currency.USD,
            exchange_rate=Decimal("1.0"),
            date=datetime.date(2026, 5, 1),
            description="Mercado semanal",
        )

    def test_registers_expense_saves_transaction(self):
        uc, acc_repo, cat_repo, tx_repo = self._make_uc()
        user_id = uuid4()
        account = _make_account(user_id=user_id)
        category = _make_category(user_id=user_id)
        acc_repo.get_by_id.return_value = account
        cat_repo.get_by_id.return_value = category

        uc.execute(self._command(user_id, account.id, category.id))

        tx_repo.save.assert_called_once()
        saved_tx = tx_repo.save.call_args[0][0]
        assert saved_tx.type.value == "expense"
        assert saved_tx.amount == Decimal("50.00")
        assert saved_tx.category_id == category.id
        assert saved_tx.description == "Mercado semanal"

    def test_raises_when_account_not_found(self):
        uc, acc_repo, cat_repo, tx_repo = self._make_uc()
        acc_repo.get_by_id.return_value = None

        with pytest.raises(AccountNotFoundError):
            uc.execute(self._command(uuid4(), uuid4(), uuid4()))

        tx_repo.save.assert_not_called()

    def test_raises_when_account_belongs_to_other_user(self):
        uc, acc_repo, cat_repo, tx_repo = self._make_uc()
        account = _make_account(user_id=uuid4())  # different owner
        acc_repo.get_by_id.return_value = account

        with pytest.raises(AccountAccessForbiddenError):
            uc.execute(self._command(uuid4(), account.id, uuid4()))

        tx_repo.save.assert_not_called()

    def test_raises_when_category_not_found(self):
        uc, acc_repo, cat_repo, tx_repo = self._make_uc()
        user_id = uuid4()
        account = _make_account(user_id=user_id)
        acc_repo.get_by_id.return_value = account
        cat_repo.get_by_id.return_value = None

        with pytest.raises(ExpenseCategoryNotFoundError):
            uc.execute(self._command(user_id, account.id, uuid4()))

        tx_repo.save.assert_not_called()
