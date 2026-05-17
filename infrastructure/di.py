"""Dependency Injection container.

Wires concrete infrastructure implementations to abstract interfaces
before injecting them into use cases. All factory functions are
intentionally stateless — they create fresh instances on each call.
For performance-critical paths, introduce a request-scoped cache here.
"""

from application.use_cases.finance.create_recurring_transaction import CreateRecurringTransactionUseCase
from application.use_cases.finance.delete_recurring_transaction import DeleteRecurringTransactionUseCase
from application.use_cases.finance.execute_recurring_transactions import ExecuteRecurringTransactionsUseCase
from application.use_cases.finance.get_user_exchange_rate import GetUserExchangeRateUseCase
from application.use_cases.finance.list_recurring_transactions import ListRecurringTransactionsUseCase
from application.use_cases.finance.onboard_user import OnboardUserUseCase
from application.use_cases.finance.set_user_exchange_rate import SetUserExchangeRateUseCase
from application.use_cases.finance.categorize_expense import CategorizeExpenseUseCase
from application.use_cases.finance.delete_savings_deposit import DeleteSavingsDepositUseCase
from application.use_cases.finance.copy_budget_plan import CopyBudgetPlanUseCase
from application.use_cases.finance.create_budget_plan import CreateBudgetPlanUseCase
from application.use_cases.finance.create_savings_distribution import CreateMonthlySavingsDistributionUseCase
from application.use_cases.finance.delete_account import DeleteAccountUseCase
from application.use_cases.finance.delete_planned_item import DeletePlannedItemUseCase
from application.use_cases.finance.delete_transaction import DeleteTransactionUseCase
from application.use_cases.finance.create_expense_category import CreateExpenseCategoryUseCase
from application.use_cases.finance.get_account_balance_history import GetAccountBalanceHistoryUseCase
from application.use_cases.finance.get_annual_report import GetAnnualReportUseCase
from application.use_cases.finance.get_budget_plan import GetBudgetPlanUseCase
from application.use_cases.finance.get_budget_vs_actual_summary import GetBudgetVsActualSummaryUseCase
from application.use_cases.finance.get_cashflow_calendar import GetCashflowCalendarUseCase
from application.use_cases.finance.get_expense_breakdown import GetExpenseBreakdownUseCase
from application.use_cases.finance.get_finance_dashboard import GetFinanceDashboardUseCase
from application.use_cases.finance.get_finance_trend import GetFinanceTrendUseCase
from application.use_cases.finance.get_net_worth import GetNetWorthUseCase
from application.use_cases.finance.get_recent_transactions import GetRecentTransactionsUseCase
from application.use_cases.finance.get_savings_dashboard import GetSavingsDashboardUseCase
from application.use_cases.finance.get_savings_projection import GetSavingsProjectionUseCase
from application.use_cases.finance.get_savings_rate import GetSavingsRateUseCase
from application.use_cases.finance.get_upcoming_invoices import GetUpcomingInvoicesUseCase
from application.use_cases.finance.reverse_transaction import ReverseTransactionUseCase
from application.use_cases.finance.create_invoice import CreateInvoiceUseCase
from application.use_cases.finance.create_savings_goal import CreateSavingsGoalUseCase
from application.use_cases.finance.deposit_to_savings import DepositToSavingsUseCase
from application.use_cases.finance.edit_savings_goal import EditSavingsGoalUseCase
from application.use_cases.finance.edit_transaction import EditTransactionUseCase
from application.use_cases.finance.generate_monthly_report import GenerateMonthlyReportUseCase
from application.use_cases.finance.get_accounts_by_user import GetAccountsByUserUseCase
from application.use_cases.finance.get_expense_categories import GetExpenseCategoriesUseCase
from application.use_cases.finance.get_monthly_financial_summary import (
    GetMonthlyFinancialSummaryUseCase,
)
from application.use_cases.finance.get_savings_goal_contributions import (
    GetSavingsGoalContributionsUseCase,
)
from application.use_cases.finance.get_savings_goals import GetSavingsGoalsUseCase
from application.use_cases.finance.get_transactions_by_user import GetTransactionsByUserUseCase
from application.use_cases.finance.process_invoice import ProcessInvoiceUseCase
from application.use_cases.finance.register_account import RegisterAccountUseCase
from application.use_cases.finance.register_currency_exchange import RegisterCurrencyExchangeUseCase
from application.use_cases.finance.register_expense import RegisterExpenseUseCase
from application.use_cases.finance.register_income import RegisterIncomeUseCase
from application.use_cases.finance.set_planned_item import SetPlannedItemUseCase
from application.use_cases.finance.suggest_savings_distribution import SuggestSavingsDistributionUseCase
from application.use_cases.finance.update_account import UpdateAccountUseCase
from application.use_cases.users.authenticate_user import AuthenticateUserUseCase
from application.use_cases.users.change_password import ChangePasswordUseCase
from application.use_cases.users.get_user_profile import GetUserProfileUseCase
from application.use_cases.users.register_user import RegisterUserUseCase
from application.use_cases.users.reset_password_confirm import ResetPasswordConfirmUseCase
from application.use_cases.users.reset_password_request import ResetPasswordRequestUseCase
from application.use_cases.users.update_profile import UpdateProfileUseCase
from infrastructure.repositories.finance import (
    DjangoAccountRepository,
    DjangoBudgetPlanRepository,
    DjangoExpenseCategoryRepository,
    DjangoExpenseRepository,
    DjangoInvoiceRepository,
    DjangoRecurringTransactionRepository,
    DjangoSavingsDepositRepository,
    DjangoSavingsDistributionRepository,
    DjangoSavingsGoalRepository,
    DjangoTransactionRepository,
    DjangoUserExchangeRateRepository,
)
from infrastructure.repositories.user import (
    DjangoPasswordHasher,
    DjangoPasswordResetTokenRepository,
    DjangoUserRepository,
)

# --- Auth / Users ---


def get_onboard_user_use_case() -> OnboardUserUseCase:
    return OnboardUserUseCase(
        account_repo=DjangoAccountRepository(),
        category_repo=DjangoExpenseCategoryRepository(),
        savings_goal_repo=DjangoSavingsGoalRepository(),
    )


def get_register_user_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(
        user_repo=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


def get_authenticate_user_use_case() -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        user_repo=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


def get_user_profile_use_case() -> GetUserProfileUseCase:
    return GetUserProfileUseCase(user_repo=DjangoUserRepository())


def get_update_profile_use_case() -> UpdateProfileUseCase:
    return UpdateProfileUseCase(user_repo=DjangoUserRepository())


def get_change_password_use_case() -> ChangePasswordUseCase:
    return ChangePasswordUseCase(
        user_repo=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


def get_reset_password_request_use_case() -> ResetPasswordRequestUseCase:
    return ResetPasswordRequestUseCase(
        user_repo=DjangoUserRepository(),
        token_repo=DjangoPasswordResetTokenRepository(),
    )


def get_reset_password_confirm_use_case() -> ResetPasswordConfirmUseCase:
    return ResetPasswordConfirmUseCase(
        user_repo=DjangoUserRepository(),
        token_repo=DjangoPasswordResetTokenRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


# --- Finance ---


def get_register_account_use_case() -> RegisterAccountUseCase:
    return RegisterAccountUseCase(account_repo=DjangoAccountRepository())


def get_accounts_by_user_use_case() -> GetAccountsByUserUseCase:
    return GetAccountsByUserUseCase(account_repo=DjangoAccountRepository())


def get_update_account_use_case() -> UpdateAccountUseCase:
    return UpdateAccountUseCase(account_repo=DjangoAccountRepository())


def get_register_income_use_case() -> RegisterIncomeUseCase:
    return RegisterIncomeUseCase(
        account_repo=DjangoAccountRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_register_currency_exchange_use_case() -> RegisterCurrencyExchangeUseCase:
    return RegisterCurrencyExchangeUseCase(
        account_repo=DjangoAccountRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_edit_transaction_use_case() -> EditTransactionUseCase:
    return EditTransactionUseCase(
        transaction_repo=DjangoTransactionRepository(),
        user_repo=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
        account_repo=DjangoAccountRepository(),
    )


def get_create_invoice_use_case() -> CreateInvoiceUseCase:
    return CreateInvoiceUseCase(invoice_repo=DjangoInvoiceRepository())


def get_process_invoice_use_case() -> ProcessInvoiceUseCase:
    return ProcessInvoiceUseCase(
        invoice_repo=DjangoInvoiceRepository(),
        transaction_repo=DjangoTransactionRepository(),
        account_repo=DjangoAccountRepository(),
    )


def get_categorize_expense_use_case() -> CategorizeExpenseUseCase:
    return CategorizeExpenseUseCase(expense_repo=DjangoExpenseRepository())


def get_create_expense_category_use_case() -> CreateExpenseCategoryUseCase:
    return CreateExpenseCategoryUseCase(category_repo=DjangoExpenseCategoryRepository())


def get_expense_categories_use_case() -> GetExpenseCategoriesUseCase:
    return GetExpenseCategoriesUseCase(category_repo=DjangoExpenseCategoryRepository())


def get_register_expense_use_case() -> RegisterExpenseUseCase:
    return RegisterExpenseUseCase(
        account_repo=DjangoAccountRepository(),
        category_repo=DjangoExpenseCategoryRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_generate_monthly_report_use_case() -> GenerateMonthlyReportUseCase:
    return GenerateMonthlyReportUseCase(
        expense_repo=DjangoExpenseRepository(),
        invoice_repo=DjangoInvoiceRepository(),
    )


def get_monthly_financial_summary_use_case() -> GetMonthlyFinancialSummaryUseCase:
    return GetMonthlyFinancialSummaryUseCase(
        transaction_repo=DjangoTransactionRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_create_savings_goal_use_case() -> CreateSavingsGoalUseCase:
    return CreateSavingsGoalUseCase(savings_goal_repo=DjangoSavingsGoalRepository())


def get_deposit_to_savings_use_case() -> DepositToSavingsUseCase:
    from django.db import transaction

    return DepositToSavingsUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
        transaction_repo=DjangoTransactionRepository(),
        account_repo=DjangoAccountRepository(),
        atomic_context=transaction.atomic,
    )


def get_savings_goals_use_case() -> GetSavingsGoalsUseCase:
    return GetSavingsGoalsUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_edit_savings_goal_use_case() -> EditSavingsGoalUseCase:
    return EditSavingsGoalUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_delete_savings_deposit_use_case() -> DeleteSavingsDepositUseCase:
    return DeleteSavingsDepositUseCase(savings_deposit_repo=DjangoSavingsDepositRepository())


def get_savings_goal_contributions_use_case() -> GetSavingsGoalContributionsUseCase:
    return GetSavingsGoalContributionsUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_delete_transaction_use_case() -> DeleteTransactionUseCase:
    return DeleteTransactionUseCase(
        transaction_repo=DjangoTransactionRepository(),
        user_repo=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


def get_transactions_by_user_use_case() -> GetTransactionsByUserUseCase:
    return GetTransactionsByUserUseCase(transaction_repo=DjangoTransactionRepository())


def get_delete_account_use_case() -> DeleteAccountUseCase:
    return DeleteAccountUseCase(
        account_repo=DjangoAccountRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_account_balance_history_use_case() -> GetAccountBalanceHistoryUseCase:
    return GetAccountBalanceHistoryUseCase(
        account_repo=DjangoAccountRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_reverse_transaction_use_case() -> ReverseTransactionUseCase:
    return ReverseTransactionUseCase(
        transaction_repo=DjangoTransactionRepository(),
        user_repo=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


# ─────────────────────────────────────────────
# Sprint 3 — Budget Plan
# ─────────────────────────────────────────────


def get_create_budget_plan_use_case() -> CreateBudgetPlanUseCase:
    return CreateBudgetPlanUseCase(budget_plan_repo=DjangoBudgetPlanRepository())


def get_get_budget_plan_use_case() -> GetBudgetPlanUseCase:
    return GetBudgetPlanUseCase(
        budget_plan_repo=DjangoBudgetPlanRepository(),
        transaction_repo=DjangoTransactionRepository(),
        category_repo=DjangoExpenseCategoryRepository(),
    )


def get_set_planned_item_use_case() -> SetPlannedItemUseCase:
    return SetPlannedItemUseCase(budget_plan_repo=DjangoBudgetPlanRepository())


def get_budget_vs_actual_summary_use_case() -> GetBudgetVsActualSummaryUseCase:
    return GetBudgetVsActualSummaryUseCase(
        budget_plan_repo=DjangoBudgetPlanRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_delete_planned_item_use_case() -> DeletePlannedItemUseCase:
    return DeletePlannedItemUseCase(budget_plan_repo=DjangoBudgetPlanRepository())


def get_copy_budget_plan_use_case() -> CopyBudgetPlanUseCase:
    return CopyBudgetPlanUseCase(budget_plan_repo=DjangoBudgetPlanRepository())


# ─────────────────────────────────────────────
# Sprint 5 — Savings Projections
# ─────────────────────────────────────────────


def get_savings_projection_use_case() -> GetSavingsProjectionUseCase:
    return GetSavingsProjectionUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_savings_rate_use_case() -> GetSavingsRateUseCase:
    return GetSavingsRateUseCase(
        transaction_repo=DjangoTransactionRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_savings_dashboard_use_case() -> GetSavingsDashboardUseCase:
    return GetSavingsDashboardUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
        transaction_repo=DjangoTransactionRepository(),
    )


def get_create_savings_distribution_use_case() -> CreateMonthlySavingsDistributionUseCase:
    return CreateMonthlySavingsDistributionUseCase(
        distribution_repo=DjangoSavingsDistributionRepository(),
        savings_goal_repo=DjangoSavingsGoalRepository(),
    )


def get_suggest_savings_distribution_use_case() -> SuggestSavingsDistributionUseCase:
    return SuggestSavingsDistributionUseCase(
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


# ─────────────────────────────────────────────
# Sprint 6 — Dashboard Core
# ─────────────────────────────────────────────


def get_net_worth_use_case() -> GetNetWorthUseCase:
    return GetNetWorthUseCase(account_repo=DjangoAccountRepository())


def get_finance_trend_use_case() -> GetFinanceTrendUseCase:
    return GetFinanceTrendUseCase(transaction_repo=DjangoTransactionRepository())


def get_expense_breakdown_use_case() -> GetExpenseBreakdownUseCase:
    return GetExpenseBreakdownUseCase(
        transaction_repo=DjangoTransactionRepository(),
        category_repo=DjangoExpenseCategoryRepository(),
    )


def get_upcoming_invoices_use_case() -> GetUpcomingInvoicesUseCase:
    return GetUpcomingInvoicesUseCase(invoice_repo=DjangoInvoiceRepository())


def get_recent_transactions_use_case() -> GetRecentTransactionsUseCase:
    return GetRecentTransactionsUseCase(transaction_repo=DjangoTransactionRepository())


def get_finance_dashboard_use_case() -> GetFinanceDashboardUseCase:
    return GetFinanceDashboardUseCase(
        account_repo=DjangoAccountRepository(),
        transaction_repo=DjangoTransactionRepository(),
        savings_goal_repo=DjangoSavingsGoalRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
        invoice_repo=DjangoInvoiceRepository(),
        budget_plan_repo=DjangoBudgetPlanRepository(),
        category_repo=DjangoExpenseCategoryRepository(),
    )


# ─────────────────────────────────────────────
# Sprint 7 — Reports
# ─────────────────────────────────────────────


def get_annual_report_use_case() -> GetAnnualReportUseCase:
    return GetAnnualReportUseCase(
        transaction_repo=DjangoTransactionRepository(),
        savings_deposit_repo=DjangoSavingsDepositRepository(),
    )


def get_cashflow_calendar_use_case() -> GetCashflowCalendarUseCase:
    return GetCashflowCalendarUseCase(transaction_repo=DjangoTransactionRepository())


# ─────────────────────────────────────────────
# DH10 — User exchange rates
# ─────────────────────────────────────────────


def get_user_exchange_rate_use_case() -> GetUserExchangeRateUseCase:
    return GetUserExchangeRateUseCase(rate_repo=DjangoUserExchangeRateRepository())


def get_set_user_exchange_rate_use_case() -> SetUserExchangeRateUseCase:
    return SetUserExchangeRateUseCase(rate_repo=DjangoUserExchangeRateRepository())


# ─────────────────────────────────────────────
# F10 — Recurring transactions
# ─────────────────────────────────────────────


def get_create_recurring_transaction_use_case() -> CreateRecurringTransactionUseCase:
    return CreateRecurringTransactionUseCase(
        rt_repo=DjangoRecurringTransactionRepository(),
        account_repo=DjangoAccountRepository(),
    )


def get_list_recurring_transactions_use_case() -> ListRecurringTransactionsUseCase:
    return ListRecurringTransactionsUseCase(rt_repo=DjangoRecurringTransactionRepository())


def get_delete_recurring_transaction_use_case() -> DeleteRecurringTransactionUseCase:
    return DeleteRecurringTransactionUseCase(rt_repo=DjangoRecurringTransactionRepository())


def get_execute_recurring_transactions_use_case() -> ExecuteRecurringTransactionsUseCase:
    return ExecuteRecurringTransactionsUseCase(
        rt_repo=DjangoRecurringTransactionRepository(),
        transaction_repo=DjangoTransactionRepository(),
        account_repo=DjangoAccountRepository(),
    )
