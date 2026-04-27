from uuid import UUID

from ninja import Router

from adapters.api.finance.schemas import (
    CategorizeExpenseRequest,
    CreateInvoiceRequest,
    ExpenseCategorizedResponseSchema,
    InvoiceCreatedResponseSchema,
    InvoiceProcessedResponseSchema,
    MonthlyReportResponseSchema,
)
from application.dtos.finance import GenerateMonthlyReportQuery, ProcessInvoiceCommand
from infrastructure.di import (
    get_categorize_expense_use_case,
    get_create_invoice_use_case,
    get_generate_monthly_report_use_case,
    get_process_invoice_use_case,
)

router = Router(tags=["Finance"])


@router.post("/invoices", response=InvoiceCreatedResponseSchema)
def create_invoice(request, payload: CreateInvoiceRequest):
    uc = get_create_invoice_use_case()
    return uc.execute(payload.to_command()).model_dump()


@router.post("/invoices/{invoice_id}/process", response=InvoiceProcessedResponseSchema)
def process_invoice(request, invoice_id: UUID):
    uc = get_process_invoice_use_case()
    return uc.execute(ProcessInvoiceCommand(invoice_id=invoice_id)).model_dump()


@router.post("/expenses", response=ExpenseCategorizedResponseSchema)
def categorize_expense(request, payload: CategorizeExpenseRequest):
    uc = get_categorize_expense_use_case()
    return uc.execute(payload.to_command()).model_dump()


@router.get("/reports/monthly", response=MonthlyReportResponseSchema)
def monthly_report(request, year: int, month: int):
    uc = get_generate_monthly_report_use_case()
    return uc.execute(GenerateMonthlyReportQuery(year=year, month=month)).model_dump()
