from application.dtos.finance import InvoiceProcessedResponse, ProcessInvoiceCommand
from domain.entities.finance import Currency, Transaction, TransactionType
from domain.exceptions.finance import InvoiceAlreadyPaidError, InvoiceNotFoundError
from domain.repositories.finance import InvoiceRepository, TransactionRepository


class ProcessInvoiceUseCase:
    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        transaction_repo: TransactionRepository | None = None,
    ) -> None:
        self._repo = invoice_repo
        self._tx_repo = transaction_repo

    def execute(self, command: ProcessInvoiceCommand) -> InvoiceProcessedResponse:
        invoice = self._repo.get_by_id(command.invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(command.invoice_id)
        if invoice.is_paid:
            raise InvoiceAlreadyPaidError(command.invoice_id)

        paid_invoice = invoice.mark_as_paid()
        self._repo.save(paid_invoice)

        # Create the expense transaction when account context is provided
        transaction_id = None
        if self._tx_repo is not None and command.user_id and command.account_id:
            tx = Transaction(
                user_id=command.user_id,
                account_id=command.account_id,
                type=TransactionType.EXPENSE,
                amount=invoice.amount,
                currency=Currency(invoice.currency),
                exchange_rate=command.exchange_rate,
                description=f"Invoice payment: {invoice.vendor}",
                date=invoice.due_date,
            )
            self._tx_repo.save(tx)
            transaction_id = tx.id

        return InvoiceProcessedResponse(
            invoice_id=paid_invoice.id,
            status="paid",
            transaction_id=transaction_id,
        )
