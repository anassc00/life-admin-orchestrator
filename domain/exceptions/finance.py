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
