from datetime import date
from decimal import Decimal
from uuid import UUID

from ninja import Schema

from application.dtos.finance import (
    CategorizeExpenseCommand,
    CreateInvoiceCommand,
    ProcessInvoiceCommand,
)


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
