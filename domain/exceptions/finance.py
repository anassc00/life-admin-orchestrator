from uuid import UUID


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
