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
    SavingsGoal,
    Transaction,
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


class TransactionRepository(ABC):
    @abstractmethod
    def get_by_id(self, transaction_id: UUID) -> Transaction | None: ...

    @abstractmethod
    def save(self, transaction: Transaction) -> None: ...

    @abstractmethod
    def save_exchange_pair(self, tx_out: Transaction, tx_in: Transaction) -> None: ...

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> list[Transaction]: ...

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


class InvoiceRepository(ABC):
    @abstractmethod
    def get_by_id(self, invoice_id: UUID) -> Invoice | None: ...

    @abstractmethod
    def save(self, invoice: Invoice) -> None: ...

    @abstractmethod
    def list_unpaid(self) -> list[Invoice]: ...

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
    def save(self, deposit: SavingsDeposit) -> None: ...

    @abstractmethod
    def list_by_goal(self, goal_id: UUID) -> list[SavingsDeposit]: ...

    @abstractmethod
    def get_monthly_savings_usd(self, user_id: UUID, year: int, month: int) -> Decimal:
        """Return total savings deposits in USD for the given user/month."""
        ...


class BudgetPlanRepository(ABC):
    @abstractmethod
    def get_by_user_and_period(self, user_id: UUID, year: int, month: int) -> BudgetPlan | None: ...

    @abstractmethod
    def save(self, plan: BudgetPlan) -> None: ...

    @abstractmethod
    def save_planned_items(self, items: list[PlannedItem]) -> None: ...

    @abstractmethod
    def list_planned_items(self, plan_id: UUID) -> list[PlannedItem]: ...


class ExpenseCategoryRepository(ABC):
    @abstractmethod
    def get_by_id(self, category_id: UUID) -> ExpenseCategory | None: ...

    @abstractmethod
    def exists_by_name_and_user(self, name: str, user_id: UUID) -> bool: ...

    @abstractmethod
    def save(self, category: ExpenseCategory) -> None: ...

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> list[ExpenseCategory]: ...
