import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema

from application.dtos.finance import (
    CategorizeExpenseCommand,
    CreateInvoiceCommand,
)
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
    amount: Decimal | None = None
    date: datetime.date | None = None
    description: str | None = None
    exchange_rate: Decimal | None = None
    notes: str | None = None
    password: str


class TransactionEditedResponseSchema(Schema):
    transaction_id: UUID
    amount: Decimal
    date: datetime.date
    description: str | None = None
    exchange_rate: Decimal
    notes: str | None = None


class CreateInvoiceRequest(Schema):
    vendor: str
    amount: Decimal
    currency: str = "MXN"
    due_date: datetime.date

    def to_command(self) -> CreateInvoiceCommand:
        return CreateInvoiceCommand(**self.model_dump())


class InvoiceCreatedResponseSchema(Schema):
    invoice_id: UUID
    vendor: str
    amount: Decimal
    currency: str
    status: str


class InvoiceProcessedResponseSchema(Schema):
    invoice_id: UUID
    status: str


class CategorizeExpenseRequest(Schema):
    description: str
    amount: Decimal
    currency: str = "MXN"
    date: datetime.date
    category: str
    invoice_id: UUID | None = None

    def to_command(self) -> CategorizeExpenseCommand:
        return CategorizeExpenseCommand(**self.model_dump())


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


class SavingsGoalResponseSchema(Schema):
    goal_id: UUID
    user_id: UUID
    motive: str
    target_amount_usd: Decimal
    is_completed: bool


class SavingsGoalSummaryResponseSchema(Schema):
    goal_id: UUID
    motive: str
    target_amount_usd: Decimal
    deposited_usd: Decimal
    is_completed: bool


class DepositToSavingsRequest(Schema):
    goal_id: UUID
    account_id: UUID
    amount: Decimal
    currency: Currency
    date: datetime.date


class SavingsDepositResponseSchema(Schema):
    deposit_id: UUID
    goal_id: UUID
    amount: Decimal
    currency: Currency


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
