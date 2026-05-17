"""F10 — List recurring transaction definitions for the current user."""

from uuid import UUID

from domain.entities.finance import RecurringTransaction
from domain.repositories.finance import RecurringTransactionRepository


class ListRecurringTransactionsUseCase:
    def __init__(self, rt_repo: RecurringTransactionRepository) -> None:
        self._repo = rt_repo

    def execute(self, user_id: UUID) -> list[RecurringTransaction]:
        return self._repo.list_by_user(user_id)
