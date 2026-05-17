"""Tests for A1 balance cache — refresh endpoint and cache-backed list_by_user."""

import uuid
from datetime import date
from decimal import Decimal

from django.test import TestCase, TransactionTestCase

from domain.entities.finance import Account, AccountType, Currency, Transaction, TransactionType


class TestBalanceCacheViaRepo(TestCase):
    """Balance cache is kept in sync by DjangoTransactionRepository.save/delete."""

    def setUp(self):
        from infrastructure.django_app.models.user import UserModel
        from infrastructure.repositories.finance import DjangoAccountRepository

        self.user = UserModel.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            hashed_password="hashed",
        )
        account = Account(
            id=uuid.uuid4(),
            user_id=self.user.id,
            name="Test Account",
            type=AccountType.WALLET,
            supported_currencies=[Currency.USD],
            default_currencies=[Currency.USD],
        )
        DjangoAccountRepository().save(account)
        self.account_id = account.id

    def _save_tx(self, tx_type, amount, currency=Currency.USD):
        from infrastructure.repositories.finance import DjangoTransactionRepository

        tx = Transaction(
            id=uuid.uuid4(),
            user_id=self.user.id,
            account_id=self.account_id,
            type=tx_type,
            amount=amount,
            currency=currency,
            exchange_rate=Decimal("1.0"),
            date=date.today(),
        )
        DjangoTransactionRepository().save(tx)
        return tx

    def test_balance_updates_on_transaction_create(self):
        from infrastructure.repositories.finance import DjangoAccountRepository

        repo = DjangoAccountRepository()
        assert repo.list_by_user(self.user.id)[0].current_balance["USD"] == "0.00"

        self._save_tx(TransactionType.INCOME, Decimal("100.00"))

        assert repo.list_by_user(self.user.id)[0].current_balance["USD"] == "100.00"

    def test_balance_updates_on_transaction_delete(self):
        from infrastructure.repositories.finance import DjangoAccountRepository, DjangoTransactionRepository

        tx = self._save_tx(TransactionType.INCOME, Decimal("100.00"))
        repo = DjangoAccountRepository()
        assert repo.list_by_user(self.user.id)[0].current_balance["USD"] == "100.00"

        DjangoTransactionRepository().delete(tx.id)
        assert repo.list_by_user(self.user.id)[0].current_balance["USD"] == "0.00"


class TestRefreshBalancesEndpoint(TransactionTestCase):
    """POST /api/finance/accounts/refresh-balances recalculates stale caches.

    Uses TransactionTestCase (not TestCase) so setUp data is committed and
    visible to the HTTP request handler's database connection.
    """

    def setUp(self):
        from infrastructure.django_app.models.finance import AccountModel, TransactionModel
        from infrastructure.django_app.models.user import UserModel

        self.user = UserModel.objects.create(
            first_name="Test",
            last_name="User",
            email="test2@example.com",
            hashed_password="hashed",
        )
        # Create account and transactions directly via ORM to simulate a stale cache
        self.account = AccountModel.objects.create(
            user_id=self.user.id,
            name="Test Account",
            type=AccountType.WALLET.value,
            supported_currencies=[Currency.USD.value, Currency.VES.value],
            default_currencies=[Currency.USD.value],
        )
        TransactionModel.objects.create(
            user_id=self.user.id,
            account=self.account,
            type=TransactionType.INCOME.value,
            amount=Decimal("500.00"),
            currency=Currency.USD.value,
            exchange_rate=Decimal("1.0"),
            date=date.today(),
        )
        TransactionModel.objects.create(
            user_id=self.user.id,
            account=self.account,
            type=TransactionType.EXPENSE.value,
            amount=Decimal("100.00"),
            currency=Currency.USD.value,
            exchange_rate=Decimal("1.0"),
            date=date.today(),
        )

    def test_refresh_balances_endpoint_returns_updated_balances(self):
        from django.test import Client

        client = Client()
        session = client.session
        session["user_id"] = str(self.user.id)
        session.save()

        response = client.post("/api/finance/accounts/refresh-balances")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["current_balance"]["USD"] == "400.00"

    def test_refresh_balances_recalculates_all_user_accounts(self):
        from django.test import Client
        from infrastructure.django_app.models.finance import AccountModel, TransactionModel

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
            amount=Decimal("1000.00"),
            currency=Currency.VES.value,
            exchange_rate=Decimal("1.0"),
            date=date.today(),
        )

        client = Client()
        session = client.session
        session["user_id"] = str(self.user.id)
        session.save()

        response = client.post("/api/finance/accounts/refresh-balances")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        acc1 = next(a for a in data if a["name"] == "Test Account")
        acc2 = next(a for a in data if a["name"] == "Second Account")
        assert acc1["current_balance"]["USD"] == "400.00"
        assert acc2["current_balance"]["VES"] == "1000.00"
