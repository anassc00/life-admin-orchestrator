from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from domain.entities.finance import (
    Account,
    AccountType,
    BudgetPlan,
    Currency,
    Expense,
    ExpenseCategory,
    IncomeCategory,
    Invoice,
    PlannedItem,
    SavingsDeposit,
    SavingsGoal,
    Transaction,
    TransactionType,
)
from domain.repositories.finance import (
    AccountRepository,
    BudgetPlanRepository,
    ExpenseCategoryRepository,
    ExpenseRepository,
    InvoiceRepository,
    SavingsDepositRepository,
    SavingsGoalRepository,
    TransactionRepository,
)
from infrastructure.django_app.models.finance import (
    AccountModel,
    BudgetPlanModel,
    ExpenseCategoryModel,
    ExpenseModel,
    InvoiceModel,
    PlannedItemModel,
    SavingsDepositModel,
    SavingsGoalModel,
    TransactionModel,
)


class DjangoAccountRepository(AccountRepository):
    def get_by_id(self, account_id: UUID) -> Account | None:
        try:
            record = AccountModel.objects.get(pk=account_id)
            return self._to_entity(record)
        except AccountModel.DoesNotExist:
            return None

    def exists_by_name_and_user(self, name: str, user_id: UUID) -> bool:
        return AccountModel.objects.filter(name=name, user_id=user_id).exists()

    def save(self, account: Account) -> None:
        AccountModel.objects.update_or_create(
            pk=account.id,
            defaults={
                "user_id": account.user_id,
                "name": account.name,
                "type": account.type.value,
                "supported_currencies": [c.value for c in account.supported_currencies],
                "default_currencies": [c.value for c in account.default_currencies],
            },
        )

    def list_by_user(self, user_id: UUID) -> list[Account]:
        return [self._to_entity(r) for r in AccountModel.objects.filter(user_id=user_id)]

    @staticmethod
    def _to_entity(record: AccountModel) -> Account:
        return Account(
            id=record.id,
            user_id=record.user_id,
            name=record.name,
            type=AccountType(record.type),
            supported_currencies=[Currency(c) for c in record.supported_currencies],
            default_currencies=[Currency(c) for c in record.default_currencies],
        )


class DjangoTransactionRepository(TransactionRepository):
    def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        try:
            record = TransactionModel.objects.get(pk=transaction_id)
            return self._to_entity(record)
        except TransactionModel.DoesNotExist:
            return None

    def save(self, tx: Transaction) -> None:
        TransactionModel.objects.update_or_create(
            pk=tx.id,
            defaults=self._to_record(tx),
        )

    def save_exchange_pair(self, tx_out: Transaction, tx_in: Transaction) -> None:
        with transaction.atomic():
            TransactionModel.objects.update_or_create(
                pk=tx_out.id, defaults=self._to_record(tx_out)
            )
            TransactionModel.objects.update_or_create(pk=tx_in.id, defaults=self._to_record(tx_in))

    def list_by_user(self, user_id: UUID) -> list[Transaction]:
        return [
            self._to_entity(r)
            for r in TransactionModel.objects.filter(user_id=user_id).order_by(
                "-date", "-created_at"
            )
        ]

    def get_monthly_totals(self, user_id: UUID, year: int, month: int) -> tuple[Decimal, Decimal]:
        from django.db.models import Q, Sum

        result = TransactionModel.objects.filter(
            user_id=user_id,
            date__year=year,
            date__month=month,
        ).aggregate(
            income=Sum("amount", filter=Q(type=TransactionType.INCOME.value)),
            expenses=Sum("amount", filter=Q(type=TransactionType.EXPENSE.value)),
        )
        return (
            result["income"] or Decimal("0"),
            result["expenses"] or Decimal("0"),
        )

    def get_monthly_totals_usd(
        self, user_id: UUID, year: int, month: int
    ) -> tuple[Decimal, Decimal]:
        """Return (base_income_usd, expenses_usd) using amount / exchange_rate."""
        from django.db.models import DecimalField as DjDecimalField
        from django.db.models import ExpressionWrapper, F, Q, Sum

        usd_expr = ExpressionWrapper(
            F("amount") / F("exchange_rate"),
            output_field=DjDecimalField(max_digits=18, decimal_places=6),
        )
        result = TransactionModel.objects.filter(
            user_id=user_id,
            date__year=year,
            date__month=month,
        ).aggregate(
            income_usd=Sum(
                usd_expr,
                filter=Q(type=TransactionType.INCOME.value, is_base_salary=True),
            ),
            expenses_usd=Sum(
                usd_expr,
                filter=Q(type=TransactionType.EXPENSE.value),
            ),
        )
        return (
            result["income_usd"] or Decimal("0"),
            result["expenses_usd"] or Decimal("0"),
        )

    @staticmethod
    def _to_entity(record: TransactionModel) -> Transaction:
        return Transaction(
            id=record.id,
            user_id=record.user_id,
            account_id=record.account_id,
            type=TransactionType(record.type),
            amount=record.amount,
            currency=Currency(record.currency),
            exchange_rate=record.exchange_rate,
            category=IncomeCategory(record.category) if record.category else None,
            is_base_salary=record.is_base_salary,
            category_id=record.category_id,
            description=record.description,
            date=record.date,
            notes=record.notes,
            related_transaction_id=record.related_transaction_id,
        )

    @staticmethod
    def _to_record(tx: Transaction) -> dict:
        return {
            "user_id": tx.user_id,
            "account_id": tx.account_id,
            "type": tx.type.value,
            "amount": tx.amount,
            "currency": tx.currency.value,
            "exchange_rate": tx.exchange_rate,
            "category": tx.category.value if tx.category else None,
            "is_base_salary": tx.is_base_salary,
            "category_id": tx.category_id,
            "description": tx.description,
            "date": tx.date,
            "notes": tx.notes,
            "related_transaction_id": tx.related_transaction_id,
        }


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
        return [self._to_entity(r) for r in ExpenseModel.objects.filter(category=category)]

    def list_between_dates(self, start: date, end: date) -> list[Expense]:
        return [self._to_entity(r) for r in ExpenseModel.objects.filter(date__range=(start, end))]

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


class DjangoExpenseCategoryRepository(ExpenseCategoryRepository):
    def get_by_id(self, category_id: UUID) -> ExpenseCategory | None:
        try:
            record = ExpenseCategoryModel.objects.get(pk=category_id)
            return self._to_entity(record)
        except ExpenseCategoryModel.DoesNotExist:
            return None

    def exists_by_name_and_user(self, name: str, user_id: UUID) -> bool:
        return ExpenseCategoryModel.objects.filter(name=name, user_id=user_id).exists()

    def save(self, category: ExpenseCategory) -> None:
        ExpenseCategoryModel.objects.update_or_create(
            pk=category.id,
            defaults={
                "user_id": category.user_id,
                "name": category.name,
                "is_fixed_expense": category.is_fixed_expense,
                "default_amount_usd": category.default_amount_usd,
            },
        )

    def list_by_user(self, user_id: UUID) -> list[ExpenseCategory]:
        return [
            self._to_entity(r)
            for r in ExpenseCategoryModel.objects.filter(user_id=user_id).order_by("name")
        ]

    @staticmethod
    def _to_entity(record: ExpenseCategoryModel) -> ExpenseCategory:
        return ExpenseCategory(
            id=record.id,
            user_id=record.user_id,
            name=record.name,
            is_fixed_expense=record.is_fixed_expense,
            default_amount_usd=record.default_amount_usd,
        )


class DjangoSavingsGoalRepository(SavingsGoalRepository):
    def get_by_id(self, goal_id: UUID) -> SavingsGoal | None:
        try:
            record = SavingsGoalModel.objects.get(pk=goal_id)
            return self._to_entity(record)
        except SavingsGoalModel.DoesNotExist:
            return None

    def save(self, goal: SavingsGoal) -> None:
        SavingsGoalModel.objects.update_or_create(
            pk=goal.id,
            defaults={
                "user_id": goal.user_id,
                "motive": goal.motive,
                "target_amount_usd": goal.target_amount_usd,
                "is_completed": goal.is_completed,
            },
        )

    def list_by_user(self, user_id: UUID) -> list[SavingsGoal]:
        return [
            self._to_entity(r)
            for r in SavingsGoalModel.objects.filter(user_id=user_id).order_by("created_at")
        ]

    @staticmethod
    def _to_entity(record: SavingsGoalModel) -> SavingsGoal:
        return SavingsGoal(
            id=record.id,
            user_id=record.user_id,
            motive=record.motive,
            target_amount_usd=record.target_amount_usd,
            is_completed=record.is_completed,
        )


class DjangoSavingsDepositRepository(SavingsDepositRepository):
    def save(self, deposit: SavingsDeposit) -> None:
        SavingsDepositModel.objects.update_or_create(
            pk=deposit.id,
            defaults={
                "user_id": deposit.user_id,
                "goal_id": deposit.goal_id,
                "account_id": deposit.account_id,
                "amount": deposit.amount,
                "currency": deposit.currency.value,
                "date": deposit.date,
            },
        )

    def list_by_goal(self, goal_id: UUID) -> list[SavingsDeposit]:
        return [
            self._to_entity(r)
            for r in SavingsDepositModel.objects.filter(goal_id=goal_id).order_by("date")
        ]

    def get_monthly_savings_usd(self, user_id: UUID, year: int, month: int) -> Decimal:
        from django.db.models import Sum

        result = SavingsDepositModel.objects.filter(
            user_id=user_id,
            date__year=year,
            date__month=month,
        ).aggregate(total=Sum("amount"))
        return result["total"] or Decimal("0")

    @staticmethod
    def _to_entity(record: SavingsDepositModel) -> SavingsDeposit:
        return SavingsDeposit(
            id=record.id,
            user_id=record.user_id,
            goal_id=record.goal_id,
            account_id=record.account_id,
            amount=record.amount,
            currency=Currency(record.currency),
            date=record.date,
        )


class DjangoBudgetPlanRepository(BudgetPlanRepository):
    def get_by_user_and_period(
        self, user_id: UUID, year: int, month: int
    ) -> BudgetPlan | None:
        try:
            record = BudgetPlanModel.objects.get(user_id=user_id, year=year, month=month)
            return self._to_entity(record)
        except BudgetPlanModel.DoesNotExist:
            return None

    def save(self, plan: BudgetPlan) -> None:
        BudgetPlanModel.objects.update_or_create(
            pk=plan.id,
            defaults={
                "user_id": plan.user_id,
                "year": plan.year,
                "month": plan.month,
                "budget_usd": plan.budget_usd,
            },
        )

    def save_planned_items(self, items: list[PlannedItem]) -> None:
        for item in items:
            PlannedItemModel.objects.update_or_create(
                pk=item.id,
                defaults={
                    "plan_id": item.plan_id,
                    "category_id": item.category_id,
                    "planned_amount_usd": item.planned_amount_usd,
                },
            )

    def list_planned_items(self, plan_id: UUID) -> list[PlannedItem]:
        return [
            PlannedItem(
                id=r.id,
                plan_id=r.plan_id,
                category_id=r.category_id,
                planned_amount_usd=r.planned_amount_usd,
            )
            for r in PlannedItemModel.objects.filter(plan_id=plan_id)
        ]

    @staticmethod
    def _to_entity(record: BudgetPlanModel) -> BudgetPlan:
        return BudgetPlan(
            id=record.id,
            user_id=record.user_id,
            year=record.year,
            month=record.month,
            budget_usd=record.budget_usd,
        )
