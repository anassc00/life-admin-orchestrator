from domain.exceptions.finance import InvoiceAlreadyPaidError, InvoiceNotFoundError
from domain.repositories.finance import InvoiceRepository
from application.dtos.finance import ProcessInvoiceCommand, InvoiceProcessedResponse


class ProcessInvoiceUseCase:

    def __init__(self, invoice_repo: InvoiceRepository) -> None:
        self._repo = invoice_repo

    def execute(self, command: ProcessInvoiceCommand) -> InvoiceProcessedResponse:
        invoice = self._repo.get_by_id(command.invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(command.invoice_id)
        if invoice.is_paid:
            raise InvoiceAlreadyPaidError(command.invoice_id)
        paid_invoice = invoice.mark_as_paid()
        self._repo.save(paid_invoice)
        return InvoiceProcessedResponse(invoice_id=paid_invoice.id, status="paid")
