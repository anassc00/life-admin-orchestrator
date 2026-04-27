from datetime import date
from uuid import UUID

from domain.entities.finance import Expense, Invoice
from domain.repositories.finance import ExpenseRepository, InvoiceRepository
from infrastructure.django_app.models.finance import ExpenseModel, InvoiceModel


class DjangoInvoiceRepository(InvoiceRepository):

    def get_by_id(self, invoice_id: UUID) -> Invoice | None:
        try:
            record = InvoiceModel.objects.get(pk=invoice_id)
            return self._to_entity(record)
        except InvoiceModel.DoesNotExist:
            return None

    def save(self, invoice: Invoice) -> None:
        InvoiceModel.objects.update_or_create(
            pk=invoice.id,
            defaults=self._to_record(invoice),
        )

    def list_unpaid(self) -> list[Invoice]:
        return [self._to_entity(r) for r in InvoiceModel.objects.filter(is_paid=False)]

    def list_all(self) -> list[Invoice]:
        return [self._to_entity(r) for r in InvoiceModel.objects.all()]

    @staticmethod
    def _to_entity(record: InvoiceModel) -> Invoice:
        return Invoice(
            id=record.id,
            vendor=record.vendor,
            amount=record.amount,
            currency=record.currency,
            due_date=record.due_date,
            is_paid=record.is_paid,
        )

    @staticmethod
    def _to_record(invoice: Invoice) -> dict:
        return {
            "vendor": invoice.vendor,
            "amount": invoice.amount,
            "currency": invoice.currency,
            "due_date": invoice.due_date,
            "is_paid": invoice.is_paid,
        }


class DjangoExpenseRepository(ExpenseRepository):

    def get_by_id(self, expense_id: UUID) -> Expense | None:
        try:
            record = ExpenseModel.objects.get(pk=expense_id)
            return self._to_entity(record)
        except ExpenseModel.DoesNotExist:
            return None

    def save(self, expense: Expense) -> None:
        ExpenseModel.objects.update_or_create(
            pk=expense.id,
            defaults=self._to_record(expense),
        )

    def list_by_period(self, year: int, month: int) -> list[Expense]:
        return [
            self._to_entity(r)
            for r in ExpenseModel.objects.filter(date__year=year, date__month=month)
        ]

    def list_by_category(self, category: str) -> list[Expense]:
        return [
            self._to_entity(r)
            for r in ExpenseModel.objects.filter(category=category)
        ]

    def list_between_dates(self, start: date, end: date) -> list[Expense]:
        return [
            self._to_entity(r)
            for r in ExpenseModel.objects.filter(date__range=(start, end))
        ]

    @staticmethod
    def _to_entity(record: ExpenseModel) -> Expense:
        return Expense(
            id=record.id,
            description=record.description,
            amount=record.amount,
            currency=record.currency,
            category=record.category,
            date=record.date,
            invoice_id=record.invoice_id,
        )

    @staticmethod
    def _to_record(expense: Expense) -> dict:
        return {
            "description": expense.description,
            "amount": expense.amount,
            "currency": expense.currency,
            "category": expense.category,
            "date": expense.date,
            "invoice_id": expense.invoice_id,
        }
