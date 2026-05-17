"""Onboard a newly registered user with default accounts, categories and a savings goal."""
import uuid
from uuid import UUID

from domain.entities.finance import Account, AccountType, Currency, ExpenseCategory, SavingsGoal
from domain.repositories.finance import AccountRepository, ExpenseCategoryRepository, SavingsGoalRepository


_DEFAULT_ACCOUNTS = [
    {"name": "Efectivo", "type": AccountType.CASH, "currencies": [Currency.USD]},
    {"name": "Banco", "type": AccountType.BANK, "currencies": [Currency.USD]},
]

_DEFAULT_CATEGORIES = [
    {"name": "Alimentación", "is_fixed": True, "default_usd": 200.0},
    {"name": "Transporte", "is_fixed": True, "default_usd": 80.0},
    {"name": "Servicios", "is_fixed": True, "default_usd": 60.0},
    {"name": "Entretenimiento", "is_fixed": False, "default_usd": 50.0},
    {"name": "Salud", "is_fixed": False, "default_usd": 40.0},
    {"name": "Otros", "is_fixed": False, "default_usd": 30.0},
]


class OnboardUserUseCase:
    def __init__(
        self,
        account_repo: AccountRepository,
        category_repo: ExpenseCategoryRepository,
        savings_goal_repo: SavingsGoalRepository,
    ) -> None:
        self._accounts = account_repo
        self._categories = category_repo
        self._goals = savings_goal_repo

    def execute(self, user_id: UUID) -> None:
        from decimal import Decimal
        # Default accounts
        for acc in _DEFAULT_ACCOUNTS:
            account = Account(
                id=uuid.uuid4(),
                user_id=user_id,
                name=acc["name"],
                type=acc["type"],
                supported_currencies=acc["currencies"],
                default_currencies=acc["currencies"],
            )
            self._accounts.save(account)

        # Default expense categories
        for cat in _DEFAULT_CATEGORIES:
            category = ExpenseCategory(
                id=uuid.uuid4(),
                user_id=user_id,
                name=cat["name"],
                is_fixed_expense=cat["is_fixed"],
                default_amount_usd=Decimal(str(cat["default_usd"])),
            )
            self._categories.save(category)

        # Default savings goal
        goal = SavingsGoal(
            id=uuid.uuid4(),
            user_id=user_id,
            motive="Fondo de emergencia",
            target_amount_usd=Decimal("1000.00"),
            expected_monthly_contribution=Decimal("100.00"),
        )
        self._goals.save(goal)
