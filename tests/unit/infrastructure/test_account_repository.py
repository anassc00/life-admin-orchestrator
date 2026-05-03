"""Tests for account repository balance calculation."""

from datetime import date
from decimal import Decimal

from django.test import TestCase

from domain.entities.finance import AccountType, Currency, TransactionType


class TestAccountBalanceCalculation(TestCase):
    """Test that account balance is calculated correctly."""

    def setUp(self):
        # Create a test user and account
        from infrastructure.django_app.models.user import UserModel
        self.user = UserModel.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        
        from infrastructure.django_app.models.finance import AccountModel
        self.account_model = AccountModel.objects.create(
            user_id=self.user.id,
            name="Test Account",
            type=AccountType.WALLET.value,
            supported_currencies=[Currency.USD.value, Currency.VES.value],
            default_currencies=[Currency.USD.value],
        )
        self.account_id = self.account_model.id

    def _create_transaction(self, tx_type, amount, currency, date_value=None, related_id=None):
        """Helper to create a transaction in the database."""
        from infrastructure.django_app.models.finance import TransactionModel
        TransactionModel.objects.create(
            user_id=self.user.id,
            account_id=self.account_id,
            type=tx_type.value,
            amount=amount,
            currency=currency.value,
            exchange_rate=Decimal('1.0'),
            date=date_value or date.today(),
            related_transaction_id=related_id,
        )

    def test_balance_with_income_only(self):
        """Balance should equal income amount."""
        self._create_transaction(TransactionType.INCOME, Decimal('100.00'), Currency.USD)
        
        from infrastructure.repositories.finance import DjangoAccountRepository
        repo = DjangoAccountRepository()
        accounts = repo.list_by_user(self.user.id)
        
        assert len(accounts) == 1
        assert accounts[0].current_balance.get('USD') == '100.00'

    def test_balance_with_income_and_expense(self):
        """Balance should be income - expense."""
        self._create_transaction(TransactionType.INCOME, Decimal('100.00'), Currency.USD)
        self._create_transaction(TransactionType.EXPENSE, Decimal('30.00'), Currency.USD)
        
        from infrastructure.repositories.finance import DjangoAccountRepository
        repo = DjangoAccountRepository()
        accounts = repo.list_by_user(self.user.id)
        
        assert accounts[0].current_balance.get('USD') == '70.00'

    def test_balance_with_savings_added(self):
        """Savings should be added to balance (not subtracted)."""
        self._create_transaction(TransactionType.INCOME, Decimal('100.00'), Currency.USD)
        self._create_transaction(TransactionType.SAVINGS, Decimal('20.00'), Currency.USD)
        
        from infrastructure.repositories.finance import DjangoAccountRepository
        repo = DjangoAccountRepository()
        accounts = repo.list_by_user(self.user.id)
        
        # 100 (income) + 20 (savings) = 120
        assert accounts[0].current_balance.get('USD') == '120.00'

    def test_balance_with_exchange_in_and_out(self):
        """Exchange in adds, exchange out subtracts."""
        self._create_transaction(TransactionType.EXCHANGE_IN, Decimal('50.00'), Currency.USD)
        self._create_transaction(TransactionType.EXCHANGE_OUT, Decimal('20.00'), Currency.USD)
        
        from infrastructure.repositories.finance import DjangoAccountRepository
        repo = DjangoAccountRepository()
        accounts = repo.list_by_user(self.user.id)
        
        assert accounts[0].current_balance.get('USD') == '30.00'

    def test_balance_multiple_currencies(self):
        """Balance should be calculated per currency."""
        self._create_transaction(TransactionType.INCOME, Decimal('100.00'), Currency.USD)
        self._create_transaction(TransactionType.INCOME, Decimal('500.00'), Currency.VES)
        self._create_transaction(TransactionType.EXPENSE, Decimal('50.00'), Currency.VES)
        
        from infrastructure.repositories.finance import DjangoAccountRepository
        repo = DjangoAccountRepository()
        accounts = repo.list_by_user(self.user.id)
        
        assert accounts[0].current_balance.get('USD') == '100.00'
        assert accounts[0].current_balance.get('VES') == '450.00'

    def test_balance_empty_account(self):
        """Account with no transactions should have 0 balance."""
        from infrastructure.repositories.finance import DjangoAccountRepository
        repo = DjangoAccountRepository()
        accounts = repo.list_by_user(self.user.id)
        
        # Should have entries for supported currencies with 0.00
        assert accounts[0].current_balance.get('USD') == '0.00'
        assert accounts[0].current_balance.get('VES') == '0.00'

    def test_balance_negative(self):
        """Balance can be negative."""
        self._create_transaction(TransactionType.EXPENSE, Decimal('100.00'), Currency.USD)
        
        from infrastructure.repositories.finance import DjangoAccountRepository
        repo = DjangoAccountRepository()
        accounts = repo.list_by_user(self.user.id)
        
        assert accounts[0].current_balance.get('USD') == '-100.00'
