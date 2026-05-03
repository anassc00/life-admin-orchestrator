"""Tests for account balance signal triggering and refresh endpoint."""

from datetime import date
from decimal import Decimal

from django.test import TestCase

from domain.entities.finance import AccountType, Currency, TransactionType
from infrastructure.django_app.models.finance import AccountModel, TransactionModel
from infrastructure.django_app.models.user import UserModel


class TestBalanceSignalTrigger(TestCase):
    """Test that balances are recalculated when transactions are created/edited/deleted."""

    def setUp(self):
        self.user = UserModel.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            hashed_password="hashed",
        )
        self.account = AccountModel.objects.create(
            user_id=self.user.id,
            name="Test Account",
            type=AccountType.WALLET.value,
            supported_currencies=[Currency.USD.value],
            default_currencies=[Currency.USD.value],
        )

    def test_balance_updates_on_transaction_create(self):
        """Creating a transaction should update the account balance."""
        # Verify initial balance is 0
        from infrastructure.repositories.finance import DjangoAccountRepository
        repo = DjangoAccountRepository()
        accounts = repo.list_by_user(self.user.id)
        assert accounts[0].current_balance['USD'] == '0.00'

        # Create a transaction
        TransactionModel.objects.create(
            user_id=self.user.id,
            account=self.account,
            type=TransactionType.INCOME.value,
            amount=Decimal('100.00'),
            currency=Currency.USD.value,
            exchange_rate=Decimal('1.0'),
            date=date.today(),
        )

        # Balance should be updated automatically
        accounts = repo.list_by_user(self.user.id)
        assert accounts[0].current_balance['USD'] == '100.00'

    def test_balance_updates_on_transaction_delete(self):
        """Deleting a transaction should update the account balance."""
        # Create a transaction
        tx = TransactionModel.objects.create(
            user_id=self.user.id,
            account=self.account,
            type=TransactionType.INCOME.value,
            amount=Decimal('100.00'),
            currency=Currency.USD.value,
            exchange_rate=Decimal('1.0'),
            date=date.today(),
        )

        # Verify balance is 100
        from infrastructure.repositories.finance import DjangoAccountRepository
        repo = DjangoAccountRepository()
        accounts = repo.list_by_user(self.user.id)
        assert accounts[0].current_balance['USD'] == '100.00'

        # Delete the transaction
        tx.delete()

        # Balance should be back to 0
        accounts = repo.list_by_user(self.user.id)
        assert accounts[0].current_balance['USD'] == '0.00'


class TestRefreshBalancesEndpoint(TestCase):
    """Test the POST /api/finance/accounts/refresh-balances endpoint."""

    def setUp(self):
        self.user = UserModel.objects.create(
            first_name="Test",
            last_name="User",
            email="test2@example.com",
            hashed_password="hashed",
        )
        self.account = AccountModel.objects.create(
            user_id=self.user.id,
            name="Test Account",
            type=AccountType.WALLET.value,
            supported_currencies=[Currency.USD.value, Currency.VES.value],
            default_currencies=[Currency.USD.value],
        )
        # Create some transactions
        TransactionModel.objects.create(
            user_id=self.user.id,
            account=self.account,
            type=TransactionType.INCOME.value,
            amount=Decimal('500.00'),
            currency=Currency.USD.value,
            exchange_rate=Decimal('1.0'),
            date=date.today(),
        )
        TransactionModel.objects.create(
            user_id=self.user.id,
            account=self.account,
            type=TransactionType.EXPENSE.value,
            amount=Decimal('100.00'),
            currency=Currency.USD.value,
            exchange_rate=Decimal('1.0'),
            date=date.today(),
        )

    def test_refresh_balances_endpoint_returns_updated_balances(self):
        """POST /refresh-balances should recalculate and return account balances."""
        from django.test import Client
        client = Client()
        # Simulate logged-in session
        session = client.session
        session['user_id'] = str(self.user.id)
        session.save()

        response = client.post('/api/finance/accounts/refresh-balances')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['current_balance']['USD'] == '400.00'

    def test_refresh_balances_recalculates_all_user_accounts(self):
        """Refresh should update all accounts for the user."""
        # Create another account
        account2 = AccountModel.objects.create(
            user_id=self.user.id,
            name="Second Account",
            type=AccountType.BANK.value,
            supported_currencies=[Currency.VES.value],
            default_currencies=[Currency.VES.value],
        )
        TransactionModel.objects.create(
            user_id=self.user.id,
            account=account2,
            type=TransactionType.INCOME.value,
            amount=Decimal('1000.00'),
            currency=Currency.VES.value,
            exchange_rate=Decimal('1.0'),
            date=date.today(),
        )

        from django.test import Client
        client = Client()
        session = client.session
        session['user_id'] = str(self.user.id)
        session.save()

        response = client.post('/api/finance/accounts/refresh-balances')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Find accounts by name
        acc1 = next(a for a in data if a['name'] == 'Test Account')
        acc2 = next(a for a in data if a['name'] == 'Second Account')
        assert acc1['current_balance']['USD'] == '400.00'
        assert acc2['current_balance']['VES'] == '1000.00'
