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
    MXN = "MXN"


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
    EXCHANGE_OUT = "exchange_out"
    EXCHANGE_IN = "exchange_in"
    SAVINGS = "savings"


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
    current_balance: dict[str, str] = {}  # currency -> balance


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
    is_base_salary: bool = False
    category_id: UUID | None = None
    description: str | None = None
    date: date
    notes: str | None = None
    related_transaction_id: UUID | None = None


class ExpenseCategory(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str
    is_fixed_expense: bool = False
    default_amount_usd: Decimal = Decimal("0")


class Invoice(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    vendor: str
    amount: Decimal
    currency: str = "MXN"
    due_date: date
    is_paid: bool = False

    def mark_as_paid(self) -> "Invoice":
        return self.model_copy(update={"is_paid": True})


class SavingsGoal(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    motive: str
    target_amount_usd: Decimal
    expected_monthly_contribution: Decimal = Decimal("0")
    is_completed: bool = False


class SavingsDeposit(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    goal_id: UUID
    account_id: UUID
    amount: Decimal
    currency: Currency
    date: date
    notes: str | None = None


class BudgetPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    year: int
    month: int
    budget_usd: Decimal = Decimal("500")


class PlannedItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    plan_id: UUID
    category_id: UUID | None = None  # None = savings bucket
    planned_amount_usd: Decimal


class Expense(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    description: str
    amount: Decimal
    currency: str = "MXN"
    category: str
    date: date
    invoice_id: UUID | None = None
