from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("life_admin", "0007_add_password_reset_token"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoicemodel",
            name="user_id",
            field=models.UUIDField(db_index=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="expensemodel",
            name="user_id",
            field=models.UUIDField(db_index=True, null=True, blank=True),
        ),
    ]
