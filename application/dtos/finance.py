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
    date: date
    notes: str | None = None


class IncomeRegisteredResponse(BaseModel):
    transaction_id: UUID
    type: TransactionType
    amount: Decimal
    currency: Currency
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
    notes: str | None = None


class TransactionEditedResponse(BaseModel):
    transaction_id: UUID
    notes: str | None = None


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
