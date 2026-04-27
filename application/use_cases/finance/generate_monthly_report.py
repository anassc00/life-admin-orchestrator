from decimal import Decimal

from domain.repositories.finance import ExpenseRepository, InvoiceRepository
from application.dtos.finance import GenerateMonthlyReportQuery, MonthlyReportResponse


class GenerateMonthlyReportUseCase:

    def __init__(
        self,
        expense_repo: ExpenseRepository,
        invoice_repo: InvoiceRepository,
    ) -> None:
        self._expense_repo = expense_repo
        self._invoice_repo = invoice_repo

    def execute(self, query: GenerateMonthlyReportQuery) -> MonthlyReportResponse:
        expenses = self._expense_repo.list_by_period(query.year, query.month)
        invoices = self._invoice_repo.list_all()
        unpaid = self._invoice_repo.list_unpaid()

        total_expenses = sum((e.amount for e in expenses), Decimal("0"))

        by_category: dict[str, Decimal] = {}
        for expense in expenses:
            by_category[expense.category] = (
                by_category.get(expense.category, Decimal("0")) + expense.amount
            )

        return MonthlyReportResponse(
            year=query.year,
            month=query.month,
            total_expenses=total_expenses,
            total_invoices=len(invoices),
            unpaid_invoices=len(unpaid),
            expenses_by_category=by_category,
        )
