"""Sprint 4 + SA3 model changes.

Changes:
- SavingsGoalModel: add deadline (DateField), priority (IntegerField), category (CharField)
- SavingsDepositModel: change goal FK on_delete from CASCADE to PROTECT
- BudgetPlanModel: add income_usd (DecimalField nullable), add composite index
- New models: SavingsDistributionPlanModel, SavingsDistributionItemModel
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("life_admin", "0009_add_db_indexes"),
    ]

    operations = [
        # SA7 — Add deadline to SavingsGoalModel
        migrations.AddField(
            model_name="savingsgoalmodel",
            name="deadline",
            field=models.DateField(blank=True, null=True),
        ),
        # SA5 — Add priority to SavingsGoalModel
        migrations.AddField(
            model_name="savingsgoalmodel",
            name="priority",
            field=models.IntegerField(default=0),
        ),
        # SA8 — Add category to SavingsGoalModel
        migrations.AddField(
            model_name="savingsgoalmodel",
            name="category",
            field=models.CharField(default="other", max_length=30),
        ),
        # SA9 — Change FK on_delete from CASCADE to PROTECT
        migrations.AlterField(
            model_name="savingsdepositmodel",
            name="goal",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="deposits",
                to="life_admin.savingsgoalmodel",
            ),
        ),
        # B8 — Add income_usd to BudgetPlanModel
        migrations.AddField(
            model_name="budgetplanmodel",
            name="income_usd",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        # A2 — Composite index for BudgetPlanModel
        migrations.AddIndex(
            model_name="budgetplanmodel",
            index=models.Index(
                fields=["user_id", "year", "month"],
                name="budget_user_period_idx",
            ),
        ),
        # SA3 — New SavingsDistributionPlanModel
        migrations.CreateModel(
            name="SavingsDistributionPlanModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("user_id", models.UUIDField(db_index=True)),
                ("year", models.IntegerField()),
                ("month", models.IntegerField()),
                (
                    "total_planned_usd",
                    models.DecimalField(decimal_places=2, max_digits=14),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "savings_distribution_plans",
                "unique_together": {("user_id", "year", "month")},
            },
        ),
        # SA3 — New SavingsDistributionItemModel
        migrations.CreateModel(
            name="SavingsDistributionItemModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="life_admin.savingsdistributionplanmodel",
                    ),
                ),
                (
                    "goal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="distribution_items",
                        to="life_admin.savingsgoalmodel",
                    ),
                ),
                (
                    "planned_usd",
                    models.DecimalField(decimal_places=2, max_digits=14),
                ),
            ],
            options={
                "db_table": "savings_distribution_items",
                "unique_together": {("plan_id", "goal_id")},
            },
        ),
    ]
