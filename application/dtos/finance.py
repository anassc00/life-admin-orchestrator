from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


# --- Invoice ---

class CreateInvoiceCommand(BaseModel):
    vendor: str
    amount: Decimal
    currency: str = "MXN"
    due_date: date


class InvoiceCreatedResponse(BaseModel):
    invoice_id: UUID
    vendor: str
    amount: Decimal
    currency: str
    status: str = "created"


class ProcessInvoiceCommand(BaseModel):
    invoice_id: UUID


class InvoiceProcessedResponse(BaseModel):
    invoice_id: UUID
    status: str


# --- Expense ---

class CategorizeExpenseCommand(BaseModel):
    description: str
    amount: Decimal
    currency: str = "MXN"
    date: date
    category: str
    invoice_id: UUID | None = None


class ExpenseCategorizedResponse(BaseModel):
    expense_id: UUID
    category: str


# --- Reports ---

class GenerateMonthlyReportQuery(BaseModel):
    year: int
    month: int


class MonthlyReportResponse(BaseModel):
    year: int
    month: int
    total_expenses: Decimal
    total_invoices: int
    unpaid_invoices: int
    expenses_by_category: dict[str, Decimal]
