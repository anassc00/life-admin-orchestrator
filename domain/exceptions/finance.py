from uuid import UUID


class AccountAlreadyExistsError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"An account named '{name}' already exists for this user.")
        self.name = name


class AccountNotFoundError(Exception):
    def __init__(self, account_id: UUID | None = None) -> None:
        msg = f"Account '{account_id}' not found." if account_id else "Account not found."
        super().__init__(msg)


class TransactionNotFoundError(Exception):
    def __init__(self, transaction_id: UUID | None = None) -> None:
        msg = (
            f"Transaction '{transaction_id}' not found."
            if transaction_id
            else "Transaction not found."
        )
        super().__init__(msg)


class AccountAccessForbiddenError(Exception):
    def __init__(self) -> None:
        super().__init__("This account does not belong to you.")


class UnauthorizedEditError(Exception):
    def __init__(self) -> None:
        super().__init__("You are not authorized to edit this transaction.")


class InvoiceNotFoundError(Exception):
    def __init__(self, invoice_id: UUID) -> None:
        super().__init__(f"Invoice {invoice_id} not found")
        self.invoice_id = invoice_id


class InvoiceAlreadyPaidError(Exception):
    def __init__(self, invoice_id: UUID) -> None:
        super().__init__(f"Invoice {invoice_id} is already paid")
        self.invoice_id = invoice_id


class ExpenseNotFoundError(Exception):
    def __init__(self, expense_id: UUID) -> None:
        super().__init__(f"Expense {expense_id} not found")
        self.expense_id = expense_id


class ExpenseCategoryNotFoundError(Exception):
    def __init__(self, category_id: UUID | None = None) -> None:
        msg = f"Expense category '{category_id}' not found." if category_id else "Expense category not found."
        super().__init__(msg)


class ExpenseCategoryAlreadyExistsError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"An expense category named '{name}' already exists for this user.")
        self.name = name


class InvalidExchangeMathError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "The exchange amounts and rate are inconsistent. "
            "Expected: amount_in ≈ amount_out × exchange_rate (within 1%)."
        )


class InvalidEditionCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid credentials. Transaction edit not authorized.")


class SavingsDepositCurrencyError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Savings deposits must come from a USD or USDT account. "
            "VES accounts are not allowed."
        )


class SavingsGoalNotFoundError(Exception):
    def __init__(self, goal_id: UUID | None = None) -> None:
        msg = f"Savings goal '{goal_id}' not found." if goal_id else "Savings goal not found."
        super().__init__(msg)
