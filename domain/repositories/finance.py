from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.entities.finance import (
    Account,
    BudgetPlan,
    Expense,
    ExpenseCategory,
    Invoice,
    PlannedItem,
    SavingsDeposit,
    SavingsDistributionPlan,
    SavingsGoal,
    Transaction,
    TransactionType,
)


class AccountRepository(ABC):
    @abstractmethod
    def get_by_id(self, account_id: UUID) -> Account | None: ...

    @abstractmethod
    def exists_by_name_and_user(self, name: str, user_id: UUID) -> bool: ...

    @abstractmethod
    def save(self, account: Account) -> None: ...

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> list[Account]: ...

    @abstractmethod
    def delete(self, account_id: UUID) -> None: ...


class TransactionRepository(ABC):
    @abstractmethod
    def get_by_id(self, transaction_id: UUID) -> Transaction | None: ...

    @abstractmethod
    def save(self, transaction: Transaction) -> None: ...

    @abstractmethod
    def save_exchange_pair(self, tx_out: Transaction, tx_in: Transaction) -> None: ...

    @abstractmethod
    def delete(self, transaction_id: UUID) -> None: ...

    @abstractmethod
    def delete_pair(self, tx_id: UUID, related_id: UUID) -> None:
        """Delete both sides of an exchange pair atomically."""
        ...

    @abstractmethod
    def list_by_user(
        self,
        user_id: UUID,
        year: int | None = None,
        month: int | None = None,
        account_id: UUID | None = None,
        tx_type: TransactionType | None = None,
        category_id: UUID | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Transaction]: ...

    @abstractmethod
    def list_by_account(
        self,
        account_id: UUID,
        year: int | None = None,
        month: int | None = None,
    ) -> list[Transaction]: ...

    @abstractmethod
    def has_transactions_for_account(self, account_id: UUID) -> bool:
        """Return True if any transaction references this account."""
        ...

    @abstractmethod
    def get_base_salary_by_period(
        self, user_id: UUID, year: int, month: int
    ) -> Transaction | None:
        """Return the base-salary income transaction for the given period, or None."""
        ...

    @abstractmethod
    def get_monthly_totals(self, user_id: UUID, year: int, month: int) -> tuple[Decimal, Decimal]:
        """Return (total_income, total_expenses) for the given user/month."""
        ...

    @abstractmethod
    def get_monthly_totals_usd(
        self, user_id: UUID, year: int, month: int
    ) -> tuple[Decimal, Decimal]:
        """Return (base_income_usd, expenses_usd) normalised via amount/exchange_rate."""
        ...

    @abstractmethod
    def get_expenses_by_category_usd(
        self, user_id: UUID, year: int, month: int
    ) -> dict[UUID | None, Decimal]:
        """Return a mapping of category_id → total_expenses_usd for the given user/month.
        category_id is None for uncategorised expenses."""
        ...

    @abstractmethod
    def get_monthly_series(
        self, user_id: UUID, months: int
    ) -> list[dict]:
        """Return the last N months of totals as a list of dicts with keys:
        year, month, income_usd, expenses_usd, savings_usd."""
        ...


class InvoiceRepository(ABC):
    @abstractmethod
    def get_by_id(self, invoice_id: UUID) -> Invoice | None: ...

    @abstractmethod
    def save(self, invoice: Invoice) -> None: ...

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> list[Invoice]: ...

    @abstractmethod
    def list_unpaid(self) -> list[Invoice]: ...

    @abstractmethod
    def list_unpaid_by_user(self, user_id: UUID) -> list[Invoice]:
        """Return all unpaid invoices for the given user, ordered by due_date asc."""
        ...

    @abstractmethod
    def list_all(self) -> list[Invoice]: ...


class ExpenseRepository(ABC):
    @abstractmethod
    def get_by_id(self, expense_id: UUID) -> Expense | None: ...

    @abstractmethod
    def save(self, expense: Expense) -> None: ...

    @abstractmethod
    def list_by_period(self, year: int, month: int) -> list[Expense]: ...

    @abstractmethod
    def list_by_category(self, category: str) -> list[Expense]: ...

    @abstractmethod
    def list_between_dates(self, start: date, end: date) -> list[Expense]: ...


class SavingsGoalRepository(ABC):
    @abstractmethod
    def get_by_id(self, goal_id: UUID) -> SavingsGoal | None: ...

    @abstractmethod
    def save(self, goal: SavingsGoal) -> None: ...

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> list[SavingsGoal]: ...


class SavingsDepositRepository(ABC):
    @abstractmethod
    def get_by_id(self, deposit_id: UUID) -> SavingsDeposit | None: ...

    @abstractmethod
    def save(self, deposit: SavingsDeposit) -> None: ...

    @abstractmethod
    def delete(self, deposit_id: UUID) -> None: ...

    @abstractmethod
    def list_by_goal(self, goal_id: UUID) -> list[SavingsDeposit]: ...

    @abstractmethod
    def get_monthly_savings_usd(self, user_id: UUID, year: int, month: int) -> Decimal:
        """Return total savings deposits in USD for the given user/month."""
        ...

    @abstractmethod
    def get_total_deposited_usd(self, goal_id: UUID) -> Decimal:
        """Return total USD deposits ever made to the given goal."""
        ...

    @abstractmethod
    def get_monthly_deposits_by_goal(
        self, user_id: UUID, year: int, month: int
    ) -> list[tuple[UUID, Decimal]]:
        """Return list of (goal_id, deposited_usd) for the given user/month."""
        ...


class BudgetPlanRepository(ABC):
    @abstractmethod
    def get_by_user_and_period(self, user_id: UUID, year: int, month: int) -> BudgetPlan | None: ...

    @abstractmethod
    def get_by_id(self, plan_id: UUID) -> BudgetPlan | None: ...

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> list[BudgetPlan]: ...

    @abstractmethod
    def save(self, plan: BudgetPlan) -> None: ...

    @abstractmethod
    def delete(self, plan_id: UUID) -> None: ...

    @abstractmethod
    def save_planned_items(self, items: list[PlannedItem]) -> None: ...

    @abstractmethod
    def list_planned_items(self, plan_id: UUID) -> list[PlannedItem]: ...

    @abstractmethod
    def delete_planned_item(self, item_id: UUID) -> None: ...

    @abstractmethod
    def get_planned_item_by_category(
        self, plan_id: UUID, category_id: UUID | None
    ) -> PlannedItem | None:
        """Return the planned item for a specific category in a plan (None = savings bucket)."""
        ...


class SavingsDistributionRepository(ABC):
    @abstractmethod
    def get_by_user_and_period(
        self, user_id: UUID, year: int, month: int
    ) -> SavingsDistributionPlan | None: ...

    @abstractmethod
    def save(self, plan: SavingsDistributionPlan) -> None: ...

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> list[SavingsDistributionPlan]: ...


class ExpenseCategoryRepository(ABC):
    @abstractmethod
    def get_by_id(self, category_id: UUID) -> ExpenseCategory | None: ...

    @abstractmethod
    def get_by_name(self, user_id: UUID, name: str) -> ExpenseCategory | None: ...

    @abstractmethod
    def exists_by_name_and_user(self, name: str, user_id: UUID) -> bool: ...

    @abstractmethod
    def save(self, category: ExpenseCategory) -> None: ...

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> list[ExpenseCategory]: ...
