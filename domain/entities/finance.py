from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class SavingsGoalCategory(StrEnum):
    EMERGENCY_FUND = "emergency_fund"
    TRAVEL = "travel"
    EDUCATION = "education"
    INVESTMENT = "investment"
    OTHER = "other"

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
    deadline: date | None = None  # SA7 — target completion date
    priority: int = 0  # SA5 — lower = higher priority (0 is top)
    category: SavingsGoalCategory = SavingsGoalCategory.OTHER  # SA8


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
    income_usd: Decimal | None = None  # B8 — expected income for 50/30/20 rule


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


# SA3 — Monthly savings distribution plan


class SavingsDistributionItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    plan_id: UUID
    goal_id: UUID
    planned_usd: Decimal


class SavingsDistributionPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    year: int
    month: int
    total_planned_usd: Decimal
    items: list[SavingsDistributionItem] = []


# DH10 — User-configured exchange rates for a given month
class UserExchangeRate(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    year: int
    month: int
    usd_ves: Decimal  # VES per 1 USD
    usd_mxn: Decimal | None = None  # MXN per 1 USD


# F10 — Recurring / scheduled transactions


class Frequency(StrEnum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"


class RecurringTransaction(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    account_id: UUID
    type: TransactionType  # INCOME or EXPENSE only
    amount: Decimal
    currency: Currency
    description: str
    category_id: UUID | None = None  # for EXPENSE
    frequency: Frequency = Frequency.MONTHLY
    # For MONTHLY: day 1-28.  For WEEKLY: 0=Mon … 6=Sun
    day: int = 1
    is_active: bool = True
    last_generated: "date | None" = None
