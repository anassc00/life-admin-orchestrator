from application.dtos.finance import CreateInvoiceCommand, InvoiceCreatedResponse
from domain.entities.finance import Invoice
from domain.repositories.finance import InvoiceRepository


class CreateInvoiceUseCase:
    def __init__(self, invoice_repo: InvoiceRepository) -> None:
        self._repo = invoice_repo

    def execute(self, command: CreateInvoiceCommand) -> InvoiceCreatedResponse:
        invoice = Invoice(
            user_id=command.user_id,
            vendor=command.vendor,
            amount=command.amount,
            currency=command.currency,
            due_date=command.due_date,
        )
        self._repo.save(invoice)
        return InvoiceCreatedResponse(
            invoice_id=invoice.id,
            vendor=invoice.vendor,
            amount=invoice.amount,
            currency=invoice.currency,
        )
