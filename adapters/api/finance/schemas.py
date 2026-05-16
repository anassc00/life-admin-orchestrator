import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema

from domain.entities.finance import AccountType, Currency, IncomeCategory, TransactionType


class RegisterAccountRequest(Schema):
    name: str
    type: AccountType
    supported_currencies: list[Currency]
    default_currencies: list[Currency]


class AccountRegisteredResponseSchema(Schema):
    account_id: UUID
    name: str
    type: AccountType


class AccountSummarySchema(Schema):
    account_id: UUID
    name: str
    type: AccountType
    supported_currencies: list[Currency]
    default_currencies: list[Currency]
    current_balance: dict[str, str] = {}  # currency -> balance


class UpdateAccountRequest(Schema):
    name: str
    type: AccountType
    supported_currencies: list[Currency]
    default_currencies: list[Currency]


class AccountUpdatedResponseSchema(Schema):
    account_id: UUID
    name: str
    type: AccountType
    supported_currencies: list[Currency]
    default_currencies: list[Currency]


class RegisterIncomeRequest(Schema):
    account_id: UUID
    amount: Decimal
    currency: Currency
    exchange_rate: Decimal
    category: IncomeCategory
    is_base_salary: bool = False
    date: datetime.date
    notes: str | None = None


class IncomeRegisteredResponseSchema(Schema):
    transaction_id: UUID
    type: TransactionType
    amount: Decimal
    currency: Currency
    is_base_salary: bool = False
    notes: str | None = None


class RegisterCurrencyExchangeRequest(Schema):
    source_account_id: UUID
    dest_account_id: UUID
    amount_out: Decimal
    currency_out: Currency
    amount_in: Decimal
    currency_in: Currency
    exchange_rate: Decimal
    date: datetime.date
    notes: str | None = None


class CurrencyExchangeRegisteredResponseSchema(Schema):
    tx_out_id: UUID
    tx_in_id: UUID
    amount_out: Decimal
    currency_out: Currency
    amount_in: Decimal
    currency_in: Currency


class EditTransactionRequest(Schema):
    account_id: UUID | None = None
    amount: Decimal | None = None
    currency: Currency | None = None
    date: datetime.date | None = None
    description: str | None = None
    exchange_rate: Decimal | None = None
    notes: str | None = None
    category_id: UUID | None = None
    password: str


class TransactionEditedResponseSchema(Schema):
    transaction_id: UUID
    account_id: UUID
    amount: Decimal
    currency: Currency
    date: datetime.date
    description: str | None = None
    exchange_rate: Decimal
    notes: str | None = None


class CreateInvoiceRequest(Schema):
    vendor: str
    amount: Decimal
    currency: str = "MXN"
    due_date: datetime.date


class InvoiceCreatedResponseSchema(Schema):
    invoice_id: UUID
    vendor: str
    amount: Decimal
    currency: str
    status: str


class InvoiceProcessedResponseSchema(Schema):
    invoice_id: UUID
    status: str
    transaction_id: UUID | None = None


class CategorizeExpenseRequest(Schema):
    description: str
    amount: Decimal
    currency: str = "MXN"
    date: datetime.date
    category: str
    invoice_id: UUID | None = None


class ExpenseCategorizedResponseSchema(Schema):
    expense_id: UUID
    category: str


class MonthlyReportResponseSchema(Schema):
    year: int
    month: int
    total_expenses: Decimal
    total_invoices: int
    unpaid_invoices: int
    expenses_by_category: dict[str, Decimal]


class MonthlyFinancialSummarySchema(Schema):
    year: int
    month: int
    total_income_usd: Decimal
    total_expenses_usd: Decimal
    total_savings_usd: Decimal
    budget_usd: Decimal
    balance_usd: Decimal


class CreateSavingsGoalRequest(Schema):
    motive: str
    target_amount_usd: Decimal
    expected_monthly_contribution: Decimal = Decimal("0")


class SavingsGoalResponseSchema(Schema):
    goal_id: UUID
    user_id: UUID
    motive: str
    target_amount_usd: Decimal
    expected_monthly_contribution: Decimal = Decimal("0")
    is_completed: bool


class SavingsGoalSummaryResponseSchema(Schema):
    goal_id: UUID
    motive: str
    target_amount_usd: Decimal
    deposited_usd: Decimal
    expected_monthly_contribution: Decimal = Decimal("0")
    is_completed: bool


class EditSavingsGoalRequest(Schema):
    motive: str | None = None
    target_amount_usd: Decimal | None = None
    expected_monthly_contribution: Decimal | None = None


class DepositToSavingsRequest(Schema):
    goal_id: UUID
    account_id: UUID
    amount: Decimal
    currency: Currency
    date: datetime.date
    notes: str | None = None


class SavingsDepositResponseSchema(Schema):
    deposit_id: UUID
    goal_id: UUID
    amount: Decimal
    currency: Currency


class SavingsDepositContributionSchema(Schema):
    deposit_id: UUID
    amount: Decimal
    currency: Currency
    date: datetime.date
    notes: str | None = None


class CreateExpenseCategoryRequest(Schema):
    name: str
    is_fixed_expense: bool = False
    default_amount_usd: Decimal = Decimal("0")


class ExpenseCategoryResponseSchema(Schema):
    category_id: UUID
    name: str
    is_fixed_expense: bool
    default_amount_usd: Decimal


class RegisterExpenseRequest(Schema):
    account_id: UUID
    category_name: str
    amount: Decimal
    currency: Currency
    exchange_rate: Decimal
    date: datetime.date
    description: str | None = None


class ExpenseRegisteredResponseSchema(Schema):
    transaction_id: UUID
    amount: Decimal
    currency: Currency
    category_id: UUID
    description: str | None = None


class DeleteTransactionRequest(Schema):
    password: str


class TransactionDeletedResponseSchema(Schema):
    transaction_id: UUID
    related_transaction_id: UUID | None = None


class AccountDeletedResponseSchema(Schema):
    account_id: UUID


class AccountBalanceHistoryItemSchema(Schema):
    year: int
    month: int
    income: Decimal
    expenses: Decimal
    net: Decimal


class AccountBalanceHistoryResponseSchema(Schema):
    account_id: UUID
    items: list[AccountBalanceHistoryItemSchema]


class ReverseTransactionRequest(Schema):
    password: str


class TransactionReversedResponseSchema(Schema):
    original_transaction_id: UUID
    reversal_transaction_id: UUID
    amount: Decimal
    currency: Currency
    date: datetime.date


class TransactionListItemSchema(Schema):
    transaction_id: UUID
    type: TransactionType
    amount: Decimal
    currency: Currency
    exchange_rate: Decimal
    category: IncomeCategory | None = None
    category_id: UUID | None = None
    description: str | None = None
    is_base_salary: bool = False
    date: datetime.date
    notes: str | None = None
    related_transaction_id: UUID | None = None


# ─────────────────────────────────────────────
# Sprint 3 — Budget
# ─────────────────────────────────────────────


class CreateBudgetPlanRequest(Schema):
    year: int
    month: int
    budget_usd: Decimal = Decimal("500")
    income_usd: Decimal | None = None


class BudgetPlanCreatedSchema(Schema):
    plan_id: UUID
    user_id: UUID
    year: int
    month: int
    budget_usd: Decimal
    income_usd: Decimal | None = None


class SetPlannedItemRequest(Schema):
    category_id: UUID | None = None
    planned_amount_usd: Decimal


class PlannedItemSchema(Schema):
    item_id: UUID
    plan_id: UUID
    category_id: UUID | None
    planned_amount_usd: Decimal


class BudgetPlanItemDetailSchema(Schema):
    item_id: UUID
    category_id: UUID | None
    category_name: str | None
    planned_usd: Decimal
    actual_usd: Decimal
    deviation_usd: Decimal
    deviation_pct: Decimal
    over_budget: bool


class BudgetPlanDetailSchema(Schema):
    plan_id: UUID
    user_id: UUID
    year: int
    month: int
    budget_usd: Decimal
    income_usd: Decimal | None
    total_planned_usd: Decimal
    total_actual_usd: Decimal
    items: list[BudgetPlanItemDetailSchema]
    rule_50_30_20: dict | None = None


class BudgetVsActualSummarySchema(Schema):
    plan_id: UUID
    year: int
    month: int
    budget_usd: Decimal
    total_planned_usd: Decimal
    total_actual_usd: Decimal
    pct_executed: Decimal
    over_budget_categories: int


# ─────────────────────────────────────────────
# Sprint 4/5 — Savings Goals (extended)
# ─────────────────────────────────────────────


class SavingsProjectionSchema(Schema):
    goal_id: UUID
    motive: str
    target_amount_usd: Decimal
    deposited_usd: Decimal
    remaining_usd: Decimal
    expected_monthly_contribution: Decimal
    months_to_completion: int | None
    projected_completion_date: datetime.date | None
    deadline: datetime.date | None
    priority: int


class SavingsRateMonthSchema(Schema):
    year: int
    month: int
    income_usd: Decimal
    savings_usd: Decimal
    rate_pct: Decimal


class SavingsRateResponseSchema(Schema):
    months: list[SavingsRateMonthSchema]
    avg_rate_pct: Decimal


class SavingsDashboardGoalSchema(Schema):
    goal_id: UUID
    motive: str
    target_amount_usd: Decimal
    deposited_usd: Decimal
    deposited_this_month_usd: Decimal
    progress_pct: Decimal
    is_completed: bool
    deadline: datetime.date | None
    priority: int


class SavingsDashboardSchema(Schema):
    year: int
    month: int
    saved_this_month_usd: Decimal
    savings_rate_pct: Decimal
    active_goals_count: int
    completed_goals_count: int
    goals: list[SavingsDashboardGoalSchema]


class SavingsDistributionItemRequest(Schema):
    goal_id: UUID
    planned_usd: Decimal


class CreateSavingsDistributionRequest(Schema):
    year: int
    month: int
    items: list[SavingsDistributionItemRequest]


class SavingsDistributionResponseSchema(Schema):
    plan_id: UUID
    year: int
    month: int
    total_planned_usd: Decimal
    items: list[dict]


class SuggestSavingsDistributionResponseSchema(Schema):
    monthly_budget_usd: Decimal
    suggestions: list[dict]


# ─────────────────────────────────────────────
# Sprint 6 — Dashboard Core
# ─────────────────────────────────────────────


class NetWorthBreakdownSchema(Schema):
    account_id: UUID
    name: str
    type: str
    balances: dict[str, str]
    usd_equivalent: Decimal


class NetWorthSchema(Schema):
    total_usd: Decimal
    cash_usd: Decimal
    bank_usd: Decimal
    wallet_usd: Decimal
    accounts: list[NetWorthBreakdownSchema]


class FinanceTrendMonthSchema(Schema):
    year: int
    month: int
    income_usd: Decimal
    expenses_usd: Decimal
    savings_usd: Decimal
    balance_usd: Decimal


class FinanceTrendSchema(Schema):
    months: list[FinanceTrendMonthSchema]


class ExpenseBreakdownItemSchema(Schema):
    category_id: UUID | None
    category_name: str | None
    total_usd: Decimal
    pct_of_total: Decimal


class ExpenseBreakdownSchema(Schema):
    year: int
    month: int
    total_expenses_usd: Decimal
    items: list[ExpenseBreakdownItemSchema]


class UpcomingInvoiceSchema(Schema):
    invoice_id: UUID
    vendor: str
    amount: Decimal
    currency: str
    due_date: datetime.date
    days_until_due: int
    is_overdue: bool


class UpcomingInvoicesSchema(Schema):
    invoices: list[UpcomingInvoiceSchema]


class FinanceDashboardSchema(Schema):
    net_worth_usd: Decimal
    monthly_summary: MonthlyFinancialSummarySchema
    budget_status: BudgetVsActualSummarySchema | None
    savings_overview: SavingsDashboardSchema
    upcoming_invoices: list[UpcomingInvoiceSchema]


# ─────────────────────────────────────────────
# Sprint 7 — Annual Report & Cashflow
# ─────────────────────────────────────────────


class AnnualReportMonthSchema(Schema):
    month: int
    income_usd: Decimal
    expenses_usd: Decimal
    savings_usd: Decimal
    balance_usd: Decimal


class AnnualReportSchema(Schema):
    year: int
    months: list[AnnualReportMonthSchema]
    total_income_usd: Decimal
    total_expenses_usd: Decimal
    total_savings_usd: Decimal
    peak_expense_month: int | None
    peak_savings_month: int | None
    dominant_category_by_quarter: dict[str, str | None]


class CashflowDaySchema(Schema):
    day: int
    date: datetime.date
    income_usd: Decimal
    expenses_usd: Decimal
    balance_usd: Decimal


class CashflowCalendarSchema(Schema):
    year: int
    month: int
    days: list[CashflowDaySchema]


# DH9 — Extended monthly summary
class ExtendedMonthlyFinancialSummarySchema(Schema):
    year: int
    month: int
    total_income_usd: Decimal
    total_expenses_usd: Decimal
    total_savings_usd: Decimal
    budget_usd: Decimal
    balance_usd: Decimal
    savings_rate_pct: Decimal
    budget_execution_pct: Decimal
    goals_active_count: int
    goals_completed_this_month: int


class SavingsDepositDeletedResponseSchema(Schema):
    deposit_id: UUID
    deleted: bool = True
