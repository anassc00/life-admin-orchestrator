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


class EditTransactionCommand(BaseModel):
    user_id: UUID
    transaction_id: UUID
    password: str
    amount: Decimal | None = None
    date: str | None = None  # Accept string, parse in use case
    description: str | None = None
    exchange_rate: Decimal | None = None
    notes: str | None = None


class TransactionEditedResponse(BaseModel):
    transaction_id: UUID
    amount: Decimal
    date: date
    description: str | None = None
    exchange_rate: Decimal
    notes: str | None = None


class GetTransactionsByUserQuery(BaseModel):
    user_id: UUID
    year: int | None = None
    month: int | None = None


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
    invoice_id: UUID


class InvoiceProcessedResponse(BaseModel):
    invoice_id: UUID
    status: str


# --- Expense ---


class CategorizeExpenseCommand(BaseModel):
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


class SavingsGoalCreatedResponse(BaseModel):
    goal_id: UUID
    user_id: UUID
    motive: str
    target_amount_usd: Decimal
    is_completed: bool = False


class SavingsGoalSummaryResponse(BaseModel):
    goal_id: UUID
    motive: str
    target_amount_usd: Decimal
    deposited_usd: Decimal
    is_completed: bool


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
