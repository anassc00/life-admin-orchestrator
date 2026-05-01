from datetime import date
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

# --- Finance Enums ---


class AccountType(StrEnum):
    CASH = "cash"
    BANK = "bank"
    WALLET = "wallet"


class Currency(StrEnum):
    VES = "VES"
    USD = "USD"
    USDT = "USDT"


class TransactionType(StrEnum):
    INCOME = "income"
    EXCHANGE_OUT = "exchange_out"
    EXCHANGE_IN = "exchange_in"


class IncomeCategory(StrEnum):
    SALARY = "salary"
    PROFESSIONAL_FEES = "professional_fees"
    OTHER_PAYMENTS = "other_payments"


# --- Finance Entities ---


class Account(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str
    type: AccountType
    supported_currencies: list[Currency]
    default_currencies: list[Currency]


class Transaction(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    account_id: UUID
    type: TransactionType
    amount: Decimal
    currency: Currency
    exchange_rate: Decimal
    category: IncomeCategory | None = None
    date: date
    notes: str | None = None
    related_transaction_id: UUID | None = None


class Invoice(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    vendor: str
    amount: Decimal
    currency: str = "MXN"
    due_date: date
    is_paid: bool = False

    def mark_as_paid(self) -> "Invoice":
        return self.model_copy(update={"is_paid": True})


class Expense(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    description: str
    amount: Decimal
    currency: str = "MXN"
    category: str
    date: date
    invoice_id: UUID | None = None
