"""Sprint 10 model changes.

Changes:
- AccountModel: add balance_cache JSONField (A1)
- New model: UserExchangeRateModel — user-configured monthly rates (DH10)
- New model: RecurringTransactionModel — recurring income/expense definitions (F10)
"""

import uuid
from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Sum


def _backfill_balance_cache(apps, schema_editor):
    """Recalculate balance for every existing account from scratch."""
    AccountModel = apps.get_model("life_admin", "AccountModel")
    TransactionModel = apps.get_model("life_admin", "TransactionModel")

    INCOME_TYPES = {"income", "exchange_in"}
    EXPENSE_TYPES = {"expense", "exchange_out"}

    for account in AccountModel.objects.all():
        cache = {}
        for currency in account.supported_currencies:
            txs = TransactionModel.objects.filter(account_id=account.id, currency=currency)
            income = (
                txs.filter(type__in=list(INCOME_TYPES)).aggregate(t=Sum("amount"))["t"]
                or Decimal("0")
            )
            expense = (
                txs.filter(type__in=list(EXPENSE_TYPES)).aggregate(t=Sum("amount"))["t"]
                or Decimal("0")
            )
            cache[currency] = str((income - expense).quantize(Decimal("0.01")))
        account.balance_cache = cache
        account.save(update_fields=["balance_cache"])


class Migration(migrations.Migration):
    dependencies = [
        ("life_admin", "0010_sprint4_model_changes"),
    ]

    operations = [
        # A1 — balance cache field on accounts
        migrations.AddField(
            model_name="accountmodel",
            name="balance_cache",
            field=models.JSONField(default=dict),
        ),
        # DH10 — user exchange rates table
        migrations.CreateModel(
            name="UserExchangeRateModel",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ("user_id", models.UUIDField(db_index=True)),
                ("year", models.IntegerField()),
                ("month", models.IntegerField()),
                ("usd_ves", models.DecimalField(max_digits=14, decimal_places=4)),
                (
                    "usd_mxn",
                    models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "user_exchange_rates"},
        ),
        migrations.AlterUniqueTogether(
            name="userexchangeratemodel",
            unique_together={("user_id", "year", "month")},
        ),
        # F10 — recurring transactions table
        migrations.CreateModel(
            name="RecurringTransactionModel",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ("user_id", models.UUIDField(db_index=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recurring_transactions",
                        to="life_admin.accountmodel",
                    ),
                ),
                ("type", models.CharField(max_length=20)),
                ("amount", models.DecimalField(max_digits=18, decimal_places=6)),
                ("currency", models.CharField(max_length=10)),
                ("description", models.CharField(max_length=500)),
                ("category_id", models.UUIDField(null=True, blank=True)),
                ("frequency", models.CharField(max_length=20, default="monthly")),
                ("day", models.IntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                ("last_generated", models.DateField(null=True, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "recurring_transactions"},
        ),
        # A1 — data migration: backfill balance_cache from existing transactions
        migrations.RunPython(
            _backfill_balance_cache,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
