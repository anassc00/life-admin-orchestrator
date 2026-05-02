from datetime import date
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
    date: date
    notes: str | None = None


class IncomeRegisteredResponseSchema(Schema):
    transaction_id: UUID
    type: TransactionType
    amount: Decimal
    currency: Currency
    notes: str | None = None


class RegisterCurrencyExchangeRequest(Schema):
    source_account_id: UUID
    dest_account_id: UUID
    amount_out: Decimal
    currency_out: Currency
    amount_in: Decimal
    currency_in: Currency
    exchange_rate: Decimal
    date: date
    notes: str | None = None


class CurrencyExchangeRegisteredResponseSchema(Schema):
    tx_out_id: UUID
    tx_in_id: UUID
    amount_out: Decimal
    currency_out: Currency
    amount_in: Decimal
    currency_in: Currency


class EditTransactionRequest(Schema):
    notes: str | None = None
    password: str


class TransactionEditedResponseSchema(Schema):
    transaction_id: UUID
    notes: str | None = None


class CreateInvoiceRequest(Schema):
    vendor: str
    amount: Decimal
    currency: str = "MXN"
    due_date: date

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
    date: date
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
    total_income: Decimal
    total_expenses: Decimal
    savings: Decimal
