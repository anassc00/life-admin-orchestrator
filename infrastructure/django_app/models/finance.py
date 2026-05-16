import uuid

from django.db import models


class AccountModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20)
    supported_currencies = models.JSONField(default=list)
    default_currencies = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts"
        unique_together = [("user_id", "name")]

    def __str__(self) -> str:
        return f"Account({self.name}, {self.type})"


class TransactionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    account = models.ForeignKey(
        AccountModel,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=18, decimal_places=6)
    currency = models.CharField(max_length=10)
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=6)
    category = models.CharField(max_length=50, null=True, blank=True)
    is_base_salary = models.BooleanField(default=False)
    category_id = models.UUIDField(null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    date = models.DateField()
    notes = models.TextField(null=True, blank=True)
    related_transaction = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_transaction",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        indexes = [
            # Covers list_by_user filtered by date range (main transactions endpoint)
            models.Index(fields=["user_id", "date"], name="tx_user_date_idx"),
            # Covers list_by_account (balance history endpoint)
            models.Index(fields=["account_id", "date"], name="tx_account_date_idx"),
        ]

    def __str__(self) -> str:
        return f"Transaction({self.type}, {self.amount} {self.currency})"


class ExpenseCategoryModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)
    is_fixed_expense = models.BooleanField(default=False)
    default_amount_usd = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "expense_categories"
        unique_together = [("user_id", "name")]

    def __str__(self) -> str:
        return f"ExpenseCategory({self.name})"


class SavingsGoalModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    motive = models.CharField(max_length=500)
    target_amount_usd = models.DecimalField(max_digits=14, decimal_places=2)
    expected_monthly_contribution = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_completed = models.BooleanField(default=False)
    deadline = models.DateField(null=True, blank=True)  # SA7
    priority = models.IntegerField(default=0)  # SA5 — lower = higher priority
    category = models.CharField(max_length=30, default="other")  # SA8
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "savings_goals"

    def __str__(self) -> str:
        return f"SavingsGoal({self.motive}, ${self.target_amount_usd})"


class SavingsDepositModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    goal = models.ForeignKey(
        SavingsGoalModel,
        on_delete=models.PROTECT,  # SA9 — prevent orphaned deposits
        related_name="deposits",
    )
    account = models.ForeignKey(
        AccountModel,
        on_delete=models.PROTECT,
        related_name="savings_deposits",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=6)
    currency = models.CharField(max_length=10)
    date = models.DateField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "savings_deposits"
        indexes = [
            # Covers get_monthly_savings_usd (user_id + date range)
            models.Index(fields=["user_id", "date"], name="deposit_user_date_idx"),
        ]

    def __str__(self) -> str:
        return f"SavingsDeposit({self.amount} {self.currency})"


class BudgetPlanModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    year = models.IntegerField()
    month = models.IntegerField()
    budget_usd = models.DecimalField(max_digits=14, decimal_places=2, default=500)
    income_usd = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)  # B8
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "budget_plans"
        unique_together = [("user_id", "year", "month")]
        indexes = [
            models.Index(fields=["user_id", "year", "month"], name="budget_user_period_idx"),
        ]

    def __str__(self) -> str:
        return f"BudgetPlan({self.year}-{self.month:02d}, ${self.budget_usd})"


class PlannedItemModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        BudgetPlanModel,
        on_delete=models.CASCADE,
        related_name="planned_items",
    )
    category_id = models.UUIDField(null=True, blank=True)
    planned_amount_usd = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = "planned_items"

    def __str__(self) -> str:
        return f"PlannedItem(${self.planned_amount_usd})"


class InvoiceModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True, null=True, blank=True)
    vendor = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="MXN")
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "invoices"

    def __str__(self) -> str:
        return f"Invoice({self.vendor}, {self.amount} {self.currency})"


class ExpenseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True, null=True, blank=True)
    description = models.TextField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="MXN")
    category = models.CharField(max_length=100)
    date = models.DateField()
    invoice = models.ForeignKey(
        InvoiceModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "expenses"

    def __str__(self) -> str:
        return f"Expense({self.category}, {self.amount} {self.currency})"


# SA3 — Monthly savings distribution plan


class SavingsDistributionPlanModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    year = models.IntegerField()
    month = models.IntegerField()
    total_planned_usd = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "savings_distribution_plans"
        unique_together = [("user_id", "year", "month")]

    def __str__(self) -> str:
        return f"SavingsDistributionPlan({self.year}-{self.month:02d}, ${self.total_planned_usd})"


class SavingsDistributionItemModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        SavingsDistributionPlanModel,
        on_delete=models.CASCADE,
        related_name="items",
    )
    goal = models.ForeignKey(
        SavingsGoalModel,
        on_delete=models.CASCADE,
        related_name="distribution_items",
    )
    planned_usd = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = "savings_distribution_items"
        unique_together = [("plan_id", "goal_id")]

    def __str__(self) -> str:
        return f"SavingsDistributionItem(${self.planned_usd})"
