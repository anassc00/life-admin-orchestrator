from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from domain.entities.finance import AccountType, Currency, IncomeCategory, TransactionType

# --- Account ---


class RegisterAccountCommand(BaseModel):
    user_id: UUID
    name: str
    type: AccountType
    supported_currencies: list[Currency]
    default_currencies: list[Currency]


class AccountRegisteredResponse(BaseModel):
    account_id: UUID
    name: str
    type: AccountType


class AccountSummaryResponse(BaseModel):
    account_id: UUID
    name: str
    type: AccountType
    supported_currencies: list[Currency]
    default_currencies: list[Currency]
    current_balance: dict[str, str] = {}


class GetAccountsByUserQuery(BaseModel):
    user_id: UUID


class UpdateAccountCommand(BaseModel):
    user_id: UUID
    account_id: UUID
    name: str
    type: AccountType
    supported_currencies: list[Currency]
    default_currencies: list[Currency]


class AccountUpdatedResponse(BaseModel):
    account_id: UUID
    name: str
    type: AccountType
    supported_currencies: list[Currency]
    default_currencies: list[Currency]


# --- Income ---


class RegisterIncomeCommand(BaseModel):
    user_id: UUID
    account_id: UUID
    amount: Decimal
    currency: Currency
    exchange_rate: Decimal
    category: IncomeCategory
    is_base_salary: bool = False
    date: date
    notes: str | None = None


class IncomeRegisteredResponse(BaseModel):
    transaction_id: UUID
    type: TransactionType
    amount: Decimal
    currency: Currency
    is_base_salary: bool = False
    notes: str | None = None


# --- Currency Exchange ---


class RegisterCurrencyExchangeCommand(BaseModel):
    user_id: UUID
    source_account_id: UUID
    dest_account_id: UUID
    amount_out: Decimal
    currency_out: Currency
    amount_in: Decimal
    currency_in: Currency
    exchange_rate: Decimal
    date: date
    notes: str | None = None


class CurrencyExchangeRegisteredResponse(BaseModel):
    tx_out_id: UUID
    tx_in_id: UUID
    amount_out: Decimal
    currency_out: Currency
    amount_in: Decimal
    currency_in: Currency


# --- Edit Transaction ---


class DeleteTransactionCommand(BaseModel):
    user_id: UUID
    transaction_id: UUID
    password: str


class TransactionDeletedResponse(BaseModel):
    transaction_id: UUID
    related_transaction_id: UUID | None = None


class EditTransactionCommand(BaseModel):
    user_id: UUID
    transaction_id: UUID
    password: str
    account_id: UUID | None = None
    amount: Decimal | None = None
    currency: Currency | None = None
    date: str | None = None  # Accept string, parse in use case
    description: str | None = None
    exchange_rate: Decimal | None = None
    notes: str | None = None
    category_id: UUID | None = None  # F5


class TransactionEditedResponse(BaseModel):
    transaction_id: UUID
    account_id: UUID
    amount: Decimal
    currency: Currency
    date: date
    description: str | None = None
    exchange_rate: Decimal
    notes: str | None = None


class GetTransactionsByUserQuery(BaseModel):
    user_id: UUID
    year: int | None = None
    month: int | None = None
    # F7 — additional filters
    account_id: UUID | None = None
    tx_type: TransactionType | None = None
    category_id: UUID | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    # F1 — pagination
    limit: int = 100
    offset: int = 0


class TransactionListItemResponse(BaseModel):
    transaction_id: UUID
    type: TransactionType
    amount: Decimal
    currency: Currency
    exchange_rate: Decimal
    category: IncomeCategory | None = None
    category_id: UUID | None = None
    description: str | None = None
    is_base_salary: bool = False
    date: date
    notes: str | None = None
    related_transaction_id: UUID | None = None


# --- Invoice ---


class CreateInvoiceCommand(BaseModel):
    user_id: UUID
    vendor: str
    amount: Decimal
    currency: str = "MXN"
    due_date: date


class InvoiceCreatedResponse(BaseModel):
    invoice_id: UUID
    vendor: str
    amount: Decimal
    currency: str
    status: str = "created"


class ProcessInvoiceCommand(BaseModel):
    user_id: UUID
    invoice_id: UUID
    # Provide account_id to create the corresponding expense transaction on payment
    account_id: UUID | None = None
    exchange_rate: Decimal = Decimal("1")


class InvoiceProcessedResponse(BaseModel):
    invoice_id: UUID
    status: str
    transaction_id: UUID | None = None


# --- Expense ---


class CategorizeExpenseCommand(BaseModel):
    user_id: UUID
    description: str
    amount: Decimal
    currency: str = "MXN"
    date: date
    category: str
    invoice_id: UUID | None = None


class ExpenseCategorizedResponse(BaseModel):
    expense_id: UUID
    category: str


# --- Monthly Financial Summary ---


class GetMonthlyFinancialSummaryQuery(BaseModel):
    user_id: UUID
    year: int
    month: int


class MonthlyFinancialSummaryResponse(BaseModel):
    year: int
    month: int
    total_income_usd: Decimal
    total_expenses_usd: Decimal
    total_savings_usd: Decimal
    budget_usd: Decimal = Decimal("500")
    balance_usd: Decimal


# --- Savings Goals ---


class CreateSavingsGoalCommand(BaseModel):
    user_id: UUID
    motive: str
    target_amount_usd: Decimal
    expected_monthly_contribution: Decimal = Decimal("0")


class SavingsGoalCreatedResponse(BaseModel):
    goal_id: UUID
    user_id: UUID
    motive: str
    target_amount_usd: Decimal
    expected_monthly_contribution: Decimal = Decimal("0")
    is_completed: bool = False


class SavingsGoalSummaryResponse(BaseModel):
    goal_id: UUID
    motive: str
    target_amount_usd: Decimal
    deposited_usd: Decimal
    expected_monthly_contribution: Decimal = Decimal("0")
    is_completed: bool


class EditSavingsGoalCommand(BaseModel):
    user_id: UUID
    goal_id: UUID
    motive: str | None = None
    target_amount_usd: Decimal | None = None
    expected_monthly_contribution: Decimal | None = None


class SavingsDepositContributionResponse(BaseModel):
    deposit_id: UUID
    amount: Decimal
    currency: Currency
    date: date
    notes: str | None = None


class GetSavingsGoalsQuery(BaseModel):
    user_id: UUID


# --- Savings Deposits ---


class DepositToSavingsCommand(BaseModel):
    user_id: UUID
    goal_id: UUID
    account_id: UUID
    amount: Decimal
    currency: Currency
    date: date
    notes: str | None = None


class SavingsDepositCreatedResponse(BaseModel):
    deposit_id: UUID
    goal_id: UUID
    amount: Decimal
    currency: Currency


# --- Budget Plan ---


class SaveBudgetPlanCommand(BaseModel):
    user_id: UUID
    year: int
    month: int
    planned_items: list["PlannedItemCommand"]


class PlannedItemCommand(BaseModel):
    category_id: UUID | None = None  # None = savings bucket
    planned_amount_usd: Decimal


class GetBudgetPlanQuery(BaseModel):
    user_id: UUID
    year: int
    month: int


class BudgetPlanResponse(BaseModel):
    plan_id: UUID
    user_id: UUID
    year: int
    month: int
    budget_usd: Decimal
    planned_items: list["PlannedItemResponse"]


class PlannedItemResponse(BaseModel):
    item_id: UUID
    category_id: UUID | None
    planned_amount_usd: Decimal


# --- Expense Categories ---


class CreateExpenseCategoryCommand(BaseModel):
    user_id: UUID
    name: str
    is_fixed_expense: bool = False
    default_amount_usd: Decimal = Decimal("0")


class ExpenseCategoryCreatedResponse(BaseModel):
    category_id: UUID
    name: str
    is_fixed_expense: bool
    default_amount_usd: Decimal


class GetExpenseCategoriesQuery(BaseModel):
    user_id: UUID


class ExpenseCategoryResponse(BaseModel):
    category_id: UUID
    name: str
    is_fixed_expense: bool
    default_amount_usd: Decimal


# --- Register Expense ---


class RegisterExpenseCommand(BaseModel):
    user_id: UUID
    account_id: UUID
    category_name: str
    amount: Decimal
    currency: Currency
    exchange_rate: Decimal
    date: date
    description: str | None = None


class ExpenseRegisteredResponse(BaseModel):
    transaction_id: UUID
    amount: Decimal
    currency: Currency
    category_id: UUID
    description: str | None = None


# --- Reports ---


class GenerateMonthlyReportQuery(BaseModel):
    year: int
    month: int


class MonthlyReportResponse(BaseModel):
    year: int
    month: int
    total_expenses: Decimal
    total_invoices: int
    unpaid_invoices: int
    expenses_by_category: dict[str, Decimal]


# --- Delete Account (F6) ---


class DeleteAccountCommand(BaseModel):
    user_id: UUID
    account_id: UUID


class AccountDeletedResponse(BaseModel):
    account_id: UUID


# --- Account Balance History (F8) ---


class GetAccountBalanceHistoryQuery(BaseModel):
    user_id: UUID
    account_id: UUID
    months: int = 6


class AccountBalanceHistoryItem(BaseModel):
    year: int
    month: int
    income: Decimal
    expenses: Decimal
    net: Decimal


class AccountBalanceHistoryResponse(BaseModel):
    account_id: UUID
    items: list[AccountBalanceHistoryItem]


# --- Reverse Transaction (F9) ---


class ReverseTransactionCommand(BaseModel):
    user_id: UUID
    transaction_id: UUID
    password: str


class TransactionReversedResponse(BaseModel):
    original_transaction_id: UUID
    reversal_transaction_id: UUID
    amount: Decimal
    currency: Currency
    date: date


# ─────────────────────────────────────────────
# SPRINT 3 — Budget Plan
# ─────────────────────────────────────────────


class CreateBudgetPlanCommand(BaseModel):
    user_id: UUID
    year: int
    month: int
    budget_usd: Decimal = Decimal("500")
    income_usd: Decimal | None = None  # B8


class BudgetPlanCreatedResponse(BaseModel):
    plan_id: UUID
    user_id: UUID
    year: int
    month: int
    budget_usd: Decimal
    income_usd: Decimal | None = None


class SetPlannedItemCommand(BaseModel):
    user_id: UUID
    plan_id: UUID
    category_id: UUID | None = None  # None = savings bucket
    planned_amount_usd: Decimal


class PlannedItemResponse(BaseModel):
    item_id: UUID
    plan_id: UUID
    category_id: UUID | None
    planned_amount_usd: Decimal


class GetBudgetPlanQuery(BaseModel):
    user_id: UUID
    year: int
    month: int


class BudgetPlanItemDetailResponse(BaseModel):
    item_id: UUID
    category_id: UUID | None
    category_name: str | None
    planned_usd: Decimal
    actual_usd: Decimal
    deviation_usd: Decimal
    deviation_pct: Decimal
    over_budget: bool  # B9


class BudgetPlanDetailResponse(BaseModel):
    plan_id: UUID
    user_id: UUID
    year: int
    month: int
    budget_usd: Decimal
    income_usd: Decimal | None
    total_planned_usd: Decimal
    total_actual_usd: Decimal
    items: list[BudgetPlanItemDetailResponse]
    rule_50_30_20: dict | None = None  # B8


class BudgetVsActualSummaryResponse(BaseModel):
    plan_id: UUID
    year: int
    month: int
    budget_usd: Decimal
    total_planned_usd: Decimal
    total_actual_usd: Decimal
    pct_executed: Decimal
    over_budget_categories: int


class DeletePlannedItemCommand(BaseModel):
    user_id: UUID
    plan_id: UUID
    category_id: UUID | None = None  # None = savings bucket


class CopyBudgetPlanCommand(BaseModel):
    user_id: UUID
    plan_id: UUID  # destination plan (current month)


# ─────────────────────────────────────────────
# SPRINT 5 — Savings Projections
# ─────────────────────────────────────────────


class SavingsProjectionResponse(BaseModel):
    goal_id: UUID
    motive: str
    target_amount_usd: Decimal
    deposited_usd: Decimal
    remaining_usd: Decimal
    expected_monthly_contribution: Decimal
    months_to_completion: int | None
    projected_completion_date: date | None
    deadline: date | None
    priority: int


class GetSavingsRateQuery(BaseModel):
    user_id: UUID
    months: int = 6


class SavingsRateMonthItem(BaseModel):
    year: int
    month: int
    income_usd: Decimal
    savings_usd: Decimal
    rate_pct: Decimal


class SavingsRateResponse(BaseModel):
    months: list[SavingsRateMonthItem]
    avg_rate_pct: Decimal


class SavingsDashboardGoalItem(BaseModel):
    goal_id: UUID
    motive: str
    target_amount_usd: Decimal
    deposited_usd: Decimal
    deposited_this_month_usd: Decimal
    progress_pct: Decimal
    is_completed: bool
    deadline: date | None
    priority: int


class SavingsDashboardResponse(BaseModel):
    year: int
    month: int
    saved_this_month_usd: Decimal
    savings_rate_pct: Decimal
    active_goals_count: int
    completed_goals_count: int
    goals: list[SavingsDashboardGoalItem]


class SavingsDistributionItemCommand(BaseModel):
    goal_id: UUID
    planned_usd: Decimal


class CreateSavingsDistributionCommand(BaseModel):
    user_id: UUID
    year: int
    month: int
    items: list[SavingsDistributionItemCommand]


class SavingsDistributionResponse(BaseModel):
    plan_id: UUID
    year: int
    month: int
    total_planned_usd: Decimal
    items: list[dict]


class SuggestSavingsDistributionResponse(BaseModel):
    monthly_budget_usd: Decimal
    suggestions: list[dict]


# ─────────────────────────────────────────────
# SPRINT 6 — Dashboard Core
# ─────────────────────────────────────────────


class NetWorthBreakdownItem(BaseModel):
    account_id: UUID
    name: str
    type: str
    balances: dict[str, str]
    usd_equivalent: Decimal


class NetWorthResponse(BaseModel):
    total_usd: Decimal
    cash_usd: Decimal
    bank_usd: Decimal
    wallet_usd: Decimal
    accounts: list[NetWorthBreakdownItem]


class FinanceTrendMonthItem(BaseModel):
    year: int
    month: int
    income_usd: Decimal
    expenses_usd: Decimal
    savings_usd: Decimal
    balance_usd: Decimal


class FinanceTrendResponse(BaseModel):
    months: list[FinanceTrendMonthItem]


class ExpenseBreakdownItem(BaseModel):
    category_id: UUID | None
    category_name: str | None
    total_usd: Decimal
    pct_of_total: Decimal


class ExpenseBreakdownResponse(BaseModel):
    year: int
    month: int
    total_expenses_usd: Decimal
    items: list[ExpenseBreakdownItem]


class UpcomingInvoiceItem(BaseModel):
    invoice_id: UUID
    vendor: str
    amount: Decimal
    currency: str
    due_date: date
    days_until_due: int
    is_overdue: bool


class UpcomingInvoicesResponse(BaseModel):
    invoices: list[UpcomingInvoiceItem]


class FinanceDashboardResponse(BaseModel):
    net_worth_usd: Decimal
    monthly_summary: "MonthlyFinancialSummaryResponse"
    budget_status: "BudgetVsActualSummaryResponse | None"
    savings_overview: "SavingsDashboardResponse"
    upcoming_invoices: list[UpcomingInvoiceItem]


# ─────────────────────────────────────────────
# SPRINT 7 — Annual Report & Cashflow
# ─────────────────────────────────────────────


class AnnualReportMonthItem(BaseModel):
    month: int
    income_usd: Decimal
    expenses_usd: Decimal
    savings_usd: Decimal
    balance_usd: Decimal


class AnnualReportResponse(BaseModel):
    year: int
    months: list[AnnualReportMonthItem]
    total_income_usd: Decimal
    total_expenses_usd: Decimal
    total_savings_usd: Decimal
    peak_expense_month: int | None
    peak_savings_month: int | None
    dominant_category_by_quarter: dict[str, str | None]


class CashflowDayItem(BaseModel):
    day: int
    date: date
    income_usd: Decimal
    expenses_usd: Decimal
    balance_usd: Decimal


class CashflowCalendarResponse(BaseModel):
    year: int
    month: int
    days: list[CashflowDayItem]


class DeleteSavingsDepositCommand(BaseModel):
    user_id: UUID
    deposit_id: UUID
