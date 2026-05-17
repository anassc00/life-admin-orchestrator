from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.db.models import Sum

from domain.entities.finance import (
    Account,
    AccountType,
    BudgetPlan,
    Currency,
    Expense,
    ExpenseCategory,
    Frequency,
    IncomeCategory,
    Invoice,
    PlannedItem,
    RecurringTransaction,
    SavingsDeposit,
    SavingsDistributionItem,
    SavingsDistributionPlan,
    SavingsGoal,
    SavingsGoalCategory,
    Transaction,
    TransactionType,
    UserExchangeRate,
)
from domain.repositories.finance import (
    AccountRepository,
    BudgetPlanRepository,
    ExpenseCategoryRepository,
    ExpenseRepository,
    InvoiceRepository,
    RecurringTransactionRepository,
    SavingsDepositRepository,
    SavingsDistributionRepository,
    SavingsGoalRepository,
    TransactionRepository,
    UserExchangeRateRepository,
)
from infrastructure.django_app.models.finance import (
    AccountModel,
    BudgetPlanModel,
    ExpenseCategoryModel,
    ExpenseModel,
    InvoiceModel,
    PlannedItemModel,
    RecurringTransactionModel,
    SavingsDepositModel,
    SavingsDistributionItemModel,
    SavingsDistributionPlanModel,
    SavingsGoalModel,
    TransactionModel,
    UserExchangeRateModel,
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

    def delete(self, account_id: UUID) -> None:
        AccountModel.objects.filter(pk=account_id).delete()

    def save(self, account: Account) -> None:
        _, created = AccountModel.objects.update_or_create(
            pk=account.id,
            defaults={
                "user_id": account.user_id,
                "name": account.name,
                "type": account.type.value,
                "supported_currencies": [c.value for c in account.supported_currencies],
                "default_currencies": [c.value for c in account.default_currencies],
            },
        )
        if created:
            # A1 — initialise cache for new accounts so list_by_user never returns stale data
            cache = {c.value: "0.00" for c in account.supported_currencies}
            AccountModel.objects.filter(pk=account.id).update(balance_cache=cache)

    def list_by_user(self, user_id: UUID) -> list[Account]:
        # A1 — read from pre-computed balance_cache instead of aggregating on every request
        return [
            self._to_entity(record, record.balance_cache or {})
            for record in AccountModel.objects.filter(user_id=user_id)
        ]

    @staticmethod
    def _to_entity(record: AccountModel, balance: dict[str, str] = None) -> Account:
        return Account(
            id=record.id,
            user_id=record.user_id,
            name=record.name,
            type=AccountType(record.type),
            supported_currencies=[Currency(c) for c in record.supported_currencies],
            default_currencies=[Currency(c) for c in record.default_currencies],
            current_balance=balance or {},
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
        self._refresh_balance_cache(tx.account_id)

    def save_exchange_pair(self, tx_out: Transaction, tx_in: Transaction) -> None:
        with transaction.atomic():
            TransactionModel.objects.update_or_create(
                pk=tx_out.id, defaults=self._to_record(tx_out)
            )
            TransactionModel.objects.update_or_create(pk=tx_in.id, defaults=self._to_record(tx_in))
        self._refresh_balance_cache(tx_out.account_id)
        self._refresh_balance_cache(tx_in.account_id)

    def delete(self, transaction_id: UUID) -> None:
        record = TransactionModel.objects.filter(pk=transaction_id).first()
        account_id = record.account_id if record else None
        TransactionModel.objects.filter(pk=transaction_id).delete()
        if account_id:
            self._refresh_balance_cache(account_id)

    def delete_pair(self, tx_id: UUID, related_id: UUID) -> None:
        r1 = TransactionModel.objects.filter(pk=tx_id).first()
        r2 = TransactionModel.objects.filter(pk=related_id).first()
        acc1 = r1.account_id if r1 else None
        acc2 = r2.account_id if r2 else None
        with transaction.atomic():
            TransactionModel.objects.filter(pk__in=[tx_id, related_id]).delete()
        if acc1:
            self._refresh_balance_cache(acc1)
        if acc2 and acc2 != acc1:
            self._refresh_balance_cache(acc2)

    @staticmethod
    def _refresh_balance_cache(account_id: UUID) -> None:
        """Recalculate and persist the balance cache for one account."""
        try:
            account = AccountModel.objects.get(pk=account_id)
        except AccountModel.DoesNotExist:
            return
        cache: dict[str, str] = {}
        for currency in account.supported_currencies:
            txs = TransactionModel.objects.filter(account_id=account_id, currency=currency)
            income = (
                txs.filter(
                    type__in=[TransactionType.INCOME.value, TransactionType.EXCHANGE_IN.value]
                ).aggregate(t=Sum("amount"))["t"]
                or Decimal("0")
            )
            expense = (
                txs.filter(
                    type__in=[TransactionType.EXPENSE.value, TransactionType.EXCHANGE_OUT.value]
                ).aggregate(t=Sum("amount"))["t"]
                or Decimal("0")
            )
            cache[currency] = str((income - expense).quantize(Decimal("0.01")))
        AccountModel.objects.filter(pk=account_id).update(balance_cache=cache)

    def list_by_user(
        self,
        user_id: UUID,
        year: int = None,
        month: int = None,
        account_id: UUID = None,
        tx_type=None,
        category_id: UUID = None,
        min_amount=None,
        max_amount=None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Transaction]:
        qs = TransactionModel.objects.filter(user_id=user_id).order_by("-date", "-created_at")
        if year is not None:
            qs = qs.filter(date__year=year)
        if month is not None:
            qs = qs.filter(date__month=month)
        if account_id is not None:
            qs = qs.filter(account_id=account_id)
        if tx_type is not None:
            qs = qs.filter(type=tx_type.value)
        if category_id is not None:
            qs = qs.filter(category_id=category_id)
        if min_amount is not None:
            qs = qs.filter(amount__gte=min_amount)
        if max_amount is not None:
            qs = qs.filter(amount__lte=max_amount)
        return [self._to_entity(r) for r in qs[offset : offset + limit]]

    def list_by_account(
        self,
        account_id: UUID,
        year: int = None,
        month: int = None,
    ) -> list[Transaction]:
        qs = TransactionModel.objects.filter(account_id=account_id).order_by("-date", "-created_at")
        if year is not None:
            qs = qs.filter(date__year=year)
        if month is not None:
            qs = qs.filter(date__month=month)
        return [self._to_entity(r) for r in qs]

    def has_transactions_for_account(self, account_id: UUID) -> bool:
        return TransactionModel.objects.filter(account_id=account_id).exists()

    def get_base_salary_by_period(
        self, user_id: UUID, year: int, month: int
    ) -> Transaction | None:
        record = TransactionModel.objects.filter(
            user_id=user_id,
            date__year=year,
            date__month=month,
            is_base_salary=True,
        ).first()
        return self._to_entity(record) if record else None

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
        from django.db.models import Case, ExpressionWrapper, F, Q, Sum, Value
        from django.db.models import DecimalField as DjDecimalField

        # Handle exchange_rate: use 1.0 if 0 or null to avoid division by zero
        safe_exchange_rate = Case(
            default=F("exchange_rate"),
            condition=Q(exchange_rate__isnull=True) | Q(exchange_rate=0),
            then=Value(1.0),
        )
        usd_expr = ExpressionWrapper(
            F("amount") / safe_exchange_rate,
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

    def get_expenses_by_category_usd(
        self, user_id: UUID, year: int, month: int
    ) -> dict[UUID | None, Decimal]:
        from django.db.models import (
            Case,
            ExpressionWrapper,
            F,
            Q,
            Sum,
            Value,
        )
        from django.db.models import DecimalField as DjDecimalField

        safe_rate = Case(
            default=F("exchange_rate"),
            condition=Q(exchange_rate__isnull=True) | Q(exchange_rate=0),
            then=Value(1.0),
        )
        usd_expr = ExpressionWrapper(
            F("amount") / safe_rate,
            output_field=DjDecimalField(max_digits=18, decimal_places=6),
        )
        rows = (
            TransactionModel.objects.filter(
                user_id=user_id,
                date__year=year,
                date__month=month,
                type=TransactionType.EXPENSE.value,
            )
            .values("category_id")
            .annotate(total_usd=Sum(usd_expr))
        )
        return {r["category_id"]: r["total_usd"] or Decimal("0") for r in rows}

    def get_monthly_series(self, user_id: UUID, months: int) -> list[dict]:
        from datetime import date

        from django.db.models import (
            Case,
            ExpressionWrapper,
            F,
            Q,
            Sum,
            Value,
        )
        from django.db.models import DecimalField as DjDecimalField

        today = date.today()
        result = []
        for i in range(months - 1, -1, -1):
            # Calculate year/month going back i months
            total_months = today.year * 12 + today.month - 1 - i
            y = total_months // 12
            m = total_months % 12 + 1

            safe_rate = Case(
                default=F("exchange_rate"),
                condition=Q(exchange_rate__isnull=True) | Q(exchange_rate=0),
                then=Value(1.0),
            )
            usd_expr = ExpressionWrapper(
                F("amount") / safe_rate,
                output_field=DjDecimalField(max_digits=18, decimal_places=6),
            )
            agg = TransactionModel.objects.filter(
                user_id=user_id,
                date__year=y,
                date__month=m,
            ).aggregate(
                income_usd=Sum(
                    usd_expr,
                    filter=Q(type=TransactionType.INCOME.value),
                ),
                expenses_usd=Sum(
                    usd_expr,
                    filter=Q(type=TransactionType.EXPENSE.value),
                ),
            )
            savings_usd = SavingsDepositModel.objects.filter(
                user_id=user_id,
                date__year=y,
                date__month=m,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

            result.append({
                "year": y,
                "month": m,
                "income_usd": agg["income_usd"] or Decimal("0"),
                "expenses_usd": agg["expenses_usd"] or Decimal("0"),
                "savings_usd": savings_usd,
            })
        return result

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

    def list_by_user(self, user_id: UUID) -> list[Invoice]:
        return [self._to_entity(r) for r in InvoiceModel.objects.filter(user_id=user_id)]

    def list_unpaid(self) -> list[Invoice]:
        return [self._to_entity(r) for r in InvoiceModel.objects.filter(is_paid=False)]

    def list_unpaid_by_user(self, user_id: UUID) -> list[Invoice]:
        return [
            self._to_entity(r)
            for r in InvoiceModel.objects.filter(user_id=user_id, is_paid=False).order_by(
                "due_date"
            )
        ]

    def list_all(self) -> list[Invoice]:
        return [self._to_entity(r) for r in InvoiceModel.objects.all()]

    @staticmethod
    def _to_entity(record: InvoiceModel) -> Invoice:
        import uuid as _uuid
        return Invoice(
            id=record.id,
            user_id=record.user_id if record.user_id else _uuid.UUID(int=0),
            vendor=record.vendor,
            amount=record.amount,
            currency=record.currency,
            due_date=record.due_date,
            is_paid=record.is_paid,
        )

    @staticmethod
    def _to_record(invoice: Invoice) -> dict:
        return {
            "user_id": invoice.user_id,
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
        import uuid as _uuid
        return Expense(
            id=record.id,
            user_id=record.user_id if record.user_id else _uuid.UUID(int=0),
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
            "user_id": expense.user_id,
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

    def get_by_name(self, user_id: UUID, name: str) -> ExpenseCategory | None:
        try:
            record = ExpenseCategoryModel.objects.get(user_id=user_id, name=name)
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
                "expected_monthly_contribution": goal.expected_monthly_contribution,
                "is_completed": goal.is_completed,
                "deadline": goal.deadline,
                "priority": goal.priority,
                "category": goal.category.value,
            },
        )

    def list_by_user(self, user_id: UUID) -> list[SavingsGoal]:
        return [
            self._to_entity(r)
            for r in SavingsGoalModel.objects.filter(user_id=user_id).order_by(
                "priority", "created_at"
            )
        ]

    @staticmethod
    def _to_entity(record: SavingsGoalModel) -> SavingsGoal:
        return SavingsGoal(
            id=record.id,
            user_id=record.user_id,
            motive=record.motive,
            target_amount_usd=record.target_amount_usd,
            expected_monthly_contribution=record.expected_monthly_contribution,
            is_completed=record.is_completed,
            deadline=record.deadline,
            priority=record.priority,
            category=SavingsGoalCategory(record.category) if record.category else SavingsGoalCategory.OTHER,
        )


class DjangoSavingsDepositRepository(SavingsDepositRepository):
    def get_by_id(self, deposit_id: UUID) -> SavingsDeposit | None:
        try:
            return self._to_entity(SavingsDepositModel.objects.get(pk=deposit_id))
        except SavingsDepositModel.DoesNotExist:
            return None

    def delete(self, deposit_id: UUID) -> None:
        SavingsDepositModel.objects.filter(pk=deposit_id).delete()

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
                "notes": deposit.notes,
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

    def get_total_deposited_usd(self, goal_id: UUID) -> Decimal:
        from django.db.models import Q, Sum

        result = SavingsDepositModel.objects.filter(
            goal_id=goal_id,
            currency=Currency.USD.value,
        ).aggregate(total=Sum("amount"))
        return result["total"] or Decimal("0")

    def get_monthly_deposits_by_goal(
        self, user_id: UUID, year: int, month: int
    ) -> list[tuple[UUID, Decimal]]:
        from django.db.models import Sum

        rows = (
            SavingsDepositModel.objects.filter(
                user_id=user_id,
                date__year=year,
                date__month=month,
            )
            .values("goal_id")
            .annotate(total=Sum("amount"))
        )
        return [(r["goal_id"], r["total"] or Decimal("0")) for r in rows]

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
            notes=record.notes,
        )


class DjangoBudgetPlanRepository(BudgetPlanRepository):
    def get_by_user_and_period(self, user_id: UUID, year: int, month: int) -> BudgetPlan | None:
        try:
            record = BudgetPlanModel.objects.get(user_id=user_id, year=year, month=month)
            return self._to_entity(record)
        except BudgetPlanModel.DoesNotExist:
            return None

    def get_by_id(self, plan_id: UUID) -> BudgetPlan | None:
        try:
            record = BudgetPlanModel.objects.get(pk=plan_id)
            return self._to_entity(record)
        except BudgetPlanModel.DoesNotExist:
            return None

    def list_by_user(self, user_id: UUID) -> list[BudgetPlan]:
        return [
            self._to_entity(r)
            for r in BudgetPlanModel.objects.filter(user_id=user_id).order_by("-year", "-month")
        ]

    def save(self, plan: BudgetPlan) -> None:
        BudgetPlanModel.objects.update_or_create(
            pk=plan.id,
            defaults={
                "user_id": plan.user_id,
                "year": plan.year,
                "month": plan.month,
                "budget_usd": plan.budget_usd,
                "income_usd": plan.income_usd,
            },
        )

    def delete(self, plan_id: UUID) -> None:
        BudgetPlanModel.objects.filter(pk=plan_id).delete()

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

    def delete_planned_item(self, item_id: UUID) -> None:
        PlannedItemModel.objects.filter(pk=item_id).delete()

    def get_planned_item_by_category(
        self, plan_id: UUID, category_id: UUID | None
    ) -> PlannedItem | None:
        try:
            if category_id is None:
                record = PlannedItemModel.objects.get(plan_id=plan_id, category_id__isnull=True)
            else:
                record = PlannedItemModel.objects.get(plan_id=plan_id, category_id=category_id)
            return PlannedItem(
                id=record.id,
                plan_id=record.plan_id,
                category_id=record.category_id,
                planned_amount_usd=record.planned_amount_usd,
            )
        except PlannedItemModel.DoesNotExist:
            return None

    @staticmethod
    def _to_entity(record: BudgetPlanModel) -> BudgetPlan:
        return BudgetPlan(
            id=record.id,
            user_id=record.user_id,
            year=record.year,
            month=record.month,
            budget_usd=record.budget_usd,
            income_usd=record.income_usd,
        )


class DjangoSavingsDistributionRepository(SavingsDistributionRepository):
    def get_by_user_and_period(
        self, user_id: UUID, year: int, month: int
    ) -> SavingsDistributionPlan | None:
        try:
            record = SavingsDistributionPlanModel.objects.prefetch_related("items").get(
                user_id=user_id, year=year, month=month
            )
            return self._to_entity(record)
        except SavingsDistributionPlanModel.DoesNotExist:
            return None

    def save(self, plan: SavingsDistributionPlan) -> None:
        from django.db import transaction as db_tx

        with db_tx.atomic():
            plan_record, _ = SavingsDistributionPlanModel.objects.update_or_create(
                pk=plan.id,
                defaults={
                    "user_id": plan.user_id,
                    "year": plan.year,
                    "month": plan.month,
                    "total_planned_usd": plan.total_planned_usd,
                },
            )
            # Replace all items
            SavingsDistributionItemModel.objects.filter(plan_id=plan.id).delete()
            for item in plan.items:
                SavingsDistributionItemModel.objects.create(
                    id=item.id,
                    plan_id=plan.id,
                    goal_id=item.goal_id,
                    planned_usd=item.planned_usd,
                )

    def list_by_user(self, user_id: UUID) -> list[SavingsDistributionPlan]:
        return [
            self._to_entity(r)
            for r in SavingsDistributionPlanModel.objects.prefetch_related("items").filter(
                user_id=user_id
            ).order_by("-year", "-month")
        ]

    @staticmethod
    def _to_entity(record: SavingsDistributionPlanModel) -> SavingsDistributionPlan:
        items = [
            SavingsDistributionItem(
                id=item.id,
                plan_id=item.plan_id,
                goal_id=item.goal_id,
                planned_usd=item.planned_usd,
            )
            for item in record.items.all()
        ]
        return SavingsDistributionPlan(
            id=record.id,
            user_id=record.user_id,
            year=record.year,
            month=record.month,
            total_planned_usd=record.total_planned_usd,
            items=items,
        )


# DH10 — User exchange rates


class DjangoUserExchangeRateRepository(UserExchangeRateRepository):
    def get_by_user_and_period(
        self, user_id: UUID, year: int, month: int
    ) -> UserExchangeRate | None:
        try:
            record = UserExchangeRateModel.objects.get(user_id=user_id, year=year, month=month)
            return self._to_entity(record)
        except UserExchangeRateModel.DoesNotExist:
            return None

    def save(self, rate: UserExchangeRate) -> None:
        UserExchangeRateModel.objects.update_or_create(
            pk=rate.id,
            defaults={
                "user_id": rate.user_id,
                "year": rate.year,
                "month": rate.month,
                "usd_ves": rate.usd_ves,
                "usd_mxn": rate.usd_mxn,
            },
        )

    def list_by_user(self, user_id: UUID) -> list[UserExchangeRate]:
        return [
            self._to_entity(r)
            for r in UserExchangeRateModel.objects.filter(user_id=user_id).order_by(
                "-year", "-month"
            )
        ]

    @staticmethod
    def _to_entity(record: UserExchangeRateModel) -> UserExchangeRate:
        return UserExchangeRate(
            id=record.id,
            user_id=record.user_id,
            year=record.year,
            month=record.month,
            usd_ves=record.usd_ves,
            usd_mxn=record.usd_mxn,
        )


# F10 — Recurring transactions


class DjangoRecurringTransactionRepository(RecurringTransactionRepository):
    def get_by_id(self, rt_id: UUID) -> RecurringTransaction | None:
        try:
            record = RecurringTransactionModel.objects.get(pk=rt_id)
            return self._to_entity(record)
        except RecurringTransactionModel.DoesNotExist:
            return None

    def save(self, rt: RecurringTransaction) -> None:
        RecurringTransactionModel.objects.update_or_create(
            pk=rt.id,
            defaults={
                "user_id": rt.user_id,
                "account_id": rt.account_id,
                "type": rt.type.value,
                "amount": rt.amount,
                "currency": rt.currency.value,
                "description": rt.description,
                "category_id": rt.category_id,
                "frequency": rt.frequency.value,
                "day": rt.day,
                "is_active": rt.is_active,
                "last_generated": rt.last_generated,
            },
        )

    def list_by_user(self, user_id: UUID) -> list[RecurringTransaction]:
        return [
            self._to_entity(r)
            for r in RecurringTransactionModel.objects.filter(user_id=user_id).order_by(
                "description"
            )
        ]

    def delete(self, rt_id: UUID) -> None:
        RecurringTransactionModel.objects.filter(pk=rt_id).delete()

    def list_active_due(self, as_of_date: "date") -> list[RecurringTransaction]:
        """Return active recurring transactions whose next fire date is <= as_of_date."""
        from datetime import date as date_type

        records = RecurringTransactionModel.objects.filter(is_active=True)
        due = []
        for record in records:
            next_fire = self._next_fire_date(record, as_of_date)
            if next_fire <= as_of_date:
                due.append(self._to_entity(record))
        return due

    @staticmethod
    def _next_fire_date(record: RecurringTransactionModel, as_of_date: "date") -> "date":
        """Calculate the next fire date for a recurring transaction."""
        from datetime import date as date_type, timedelta
        import calendar

        if record.frequency == "monthly":
            # Day of month; clamp to last day of month
            last_gen = record.last_generated
            if last_gen is None:
                # Never generated → fire on the configured day of current month
                year, month = as_of_date.year, as_of_date.month
            else:
                # Next month after last generation
                year = last_gen.year + (1 if last_gen.month == 12 else 0)
                month = 1 if last_gen.month == 12 else last_gen.month + 1
            max_day = calendar.monthrange(year, month)[1]
            day = min(record.day, max_day)
            return date_type(year, month, day)
        else:  # weekly
            # day = 0 (Mon) … 6 (Sun)
            last_gen = record.last_generated
            if last_gen is None:
                ref = as_of_date
            else:
                ref = last_gen + timedelta(days=1)
            # Find next occurrence of the configured weekday on or after ref
            days_ahead = (record.day - ref.weekday()) % 7
            return ref + timedelta(days=days_ahead)

    @staticmethod
    def _to_entity(record: RecurringTransactionModel) -> RecurringTransaction:
        return RecurringTransaction(
            id=record.id,
            user_id=record.user_id,
            account_id=record.account_id,
            type=TransactionType(record.type),
            amount=record.amount,
            currency=Currency(record.currency),
            description=record.description,
            category_id=record.category_id,
            frequency=Frequency(record.frequency),
            day=record.day,
            is_active=record.is_active,
            last_generated=record.last_generated,
        )
