from decimal import Decimal
from uuid import uuid4

import pytest

from application.use_cases.finance.onboard_user import OnboardUserUseCase
from tests.fakes.repositories import InMemoryExpenseRepository, InMemoryInvoiceRepository


def _make_repos():
    from tests.fakes.repositories import InMemorySavingsDepositRepository
    # We need simple in-memory stores for accounts, categories, and goals
    from uuid import UUID
    from domain.entities.finance import Account, ExpenseCategory, SavingsGoal

    class FakeAccountRepo:
        def __init__(self):
            self.saved = []
        def save(self, a): self.saved.append(a)
        def get_by_id(self, id): return None
        def exists_by_name_and_user(self, n, u): return False
        def list_by_user(self, u): return self.saved
        def delete(self, id): pass

    class FakeCategoryRepo:
        def __init__(self):
            self.saved = []
        def save(self, c): self.saved.append(c)
        def get_by_id(self, id): return None
        def get_by_name(self, u, n): return None
        def exists_by_name_and_user(self, n, u): return False
        def list_by_user(self, u): return self.saved

    class FakeGoalRepo:
        def __init__(self):
            self.saved = []
        def save(self, g): self.saved.append(g)
        def get_by_id(self, id): return None
        def list_by_user(self, u): return self.saved

    return FakeAccountRepo(), FakeCategoryRepo(), FakeGoalRepo()


def test_onboard_creates_default_data():
    accounts, categories, goals = _make_repos()
    uc = OnboardUserUseCase(accounts, categories, goals)
    user_id = uuid4()
    uc.execute(user_id)

    assert len(accounts.saved) == 2
    assert len(categories.saved) == 6
    assert len(goals.saved) == 1
    assert goals.saved[0].motive == "Fondo de emergencia"
    assert all(a.user_id == user_id for a in accounts.saved)
    assert all(c.user_id == user_id for c in categories.saved)
