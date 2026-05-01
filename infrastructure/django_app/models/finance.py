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

    def __str__(self) -> str:
        return f"Transaction({self.type}, {self.amount} {self.currency})"


class InvoiceModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
