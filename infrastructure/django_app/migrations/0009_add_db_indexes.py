from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("life_admin", "0008_add_user_id_to_invoice_and_expense"),
    ]

    operations = [
        # TransactionModel: (user_id, date) — covers list_by_user with date filters
        migrations.AddIndex(
            model_name="transactionmodel",
            index=models.Index(fields=["user_id", "date"], name="tx_user_date_idx"),
        ),
        # TransactionModel: (account_id, date) — covers list_by_account (balance history)
        migrations.AddIndex(
            model_name="transactionmodel",
            index=models.Index(fields=["account_id", "date"], name="tx_account_date_idx"),
        ),
        # SavingsDepositModel: (user_id, date) — covers get_monthly_savings_usd
        migrations.AddIndex(
            model_name="savingsdepositmodel",
            index=models.Index(fields=["user_id", "date"], name="deposit_user_date_idx"),
        ),
    ]
