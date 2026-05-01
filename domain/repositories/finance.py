from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from domain.entities.finance import Account, Expense, Invoice, Transaction


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
