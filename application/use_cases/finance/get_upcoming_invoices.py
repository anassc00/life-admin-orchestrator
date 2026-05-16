from datetime import date
from uuid import UUID

from application.dtos.finance import UpcomingInvoiceItem, UpcomingInvoicesResponse
from domain.repositories.finance import InvoiceRepository


class GetUpcomingInvoicesUseCase:
    """Return unpaid invoices ordered by due_date with days_until_due and is_overdue flags."""

    def __init__(self, invoice_repo: InvoiceRepository) -> None:
        self._repo = invoice_repo

    def execute(self, user_id: UUID) -> UpcomingInvoicesResponse:
        today = date.today()
        invoices = self._repo.list_unpaid_by_user(user_id)
        items = []
        for inv in invoices:
            days = (inv.due_date - today).days
            items.append(
                UpcomingInvoiceItem(
                    invoice_id=inv.id,
                    vendor=inv.vendor,
                    amount=inv.amount,
                    currency=inv.currency,
                    due_date=inv.due_date,
                    days_until_due=days,
                    is_overdue=days < 0,
                )
            )
        return UpcomingInvoicesResponse(invoices=items)
