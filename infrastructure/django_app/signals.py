"""Django signals to auto-update account balances when transactions change."""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from infrastructure.django_app.models.finance import TransactionModel


@receiver(post_save, sender=TransactionModel)
@receiver(post_delete, sender=TransactionModel)
def update_account_balance_on_transaction_change(sender, instance, **kwargs):
    """
    Trigger balance recalculation when a transaction is saved or deleted.
    The list_by_user method already calculates balances dynamically,
    so this signal ensures the next API call returns fresh data.
    """
    # The balance is calculated dynamically in the repository's list_by_user method
    # No explicit cache invalidation needed since we calculate on every call
    pass
