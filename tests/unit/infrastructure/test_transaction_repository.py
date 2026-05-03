from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from domain.entities.finance import Currency, TransactionType
from infrastructure.repositories.finance import DjangoTransactionRepository


@pytest.fixture
def repo():
    return DjangoTransactionRepository()


@pytest.fixture
def setup_transactions(db):
    """Create sample transactions for testing."""
    from infrastructure.django_app.models.finance import TransactionModel
    
    user_id = uuid4()
    account_id = uuid4()
    
    # Create transactions for different months
    txs = [
        TransactionModel(
            id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            type=TransactionType.INCOME.value,
            amount=Decimal("1000"),
            currency=Currency.USD.value,
            exchange_rate=Decimal("1"),
            date=date(2026, 5, 15),
            notes="May transaction",
        ),
        TransactionModel(
            id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            type=TransactionType.EXPENSE.value,
            amount=Decimal("500"),
            currency=Currency.USD.value,
            exchange_rate=Decimal("1"),
            date=date(2026, 4, 20),
            notes="April transaction",
        ),
        TransactionModel(
            id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            type=TransactionType.INCOME.value,
            amount=Decimal("2000"),
            currency=Currency.VES.value,
            exchange_rate=Decimal("487.12"),
            date=date(2026, 5, 10),
            notes="May VES transaction",
        ),
    ]
    
    for tx in txs:
        tx.save()
    
    yield user_id
    
    # Cleanup
    for tx in txs:
        tx.delete()


class TestListByUserWithMonthYear:
    """Test the list_by_user method with month/year filtering."""
    
    def test_list_without_filters_returns_all(self, repo, setup_transactions):
        """Should return all transactions when no month/year specified."""
        user_id = setup_transactions
        results = repo.list_by_user(user_id)
        assert len(results) == 3
    
    def test_list_with_month_year_filter(self, repo, setup_transactions):
        """Should return only transactions for specified month/year."""
        user_id = setup_transactions
        # Filter for May 2026
        results = repo.list_by_user(user_id, year=2026, month=5)
        assert len(results) == 2
        for tx in results:
            assert tx.date.year == 2026
            assert tx.date.month == 5
    
    def test_list_with_april_filter(self, repo, setup_transactions):
        """Should return only April transactions."""
        user_id = setup_transactions
        results = repo.list_by_user(user_id, year=2026, month=4)
        assert len(results) == 1
        assert results[0].date.month == 4
    
    def test_list_with_wrong_month_returns_empty(self, repo, setup_transactions):
        """Should return empty list for month with no transactions."""
        user_id = setup_transactions
        results = repo.list_by_user(user_id, year=2026, month=12)
        assert len(results) == 0
