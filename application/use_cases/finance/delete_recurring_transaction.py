"""F10 — Delete a recurring transaction definition."""

from uuid import UUID

from domain.exceptions.finance import (
    RecurringTransactionAccessForbiddenError,
    RecurringTransactionNotFoundError,
)
from domain.repositories.finance import RecurringTransactionRepository


class DeleteRecurringTransactionCommand:
    def __init__(self, user_id: UUID, rt_id: UUID) -> None:
        self.user_id = user_id
        self.rt_id = rt_id


class DeleteRecurringTransactionUseCase:
    def __init__(self, rt_repo: RecurringTransactionRepository) -> None:
        self._repo = rt_repo

    def execute(self, cmd: DeleteRecurringTransactionCommand) -> None:
        rt = self._repo.get_by_id(cmd.rt_id)
        if rt is None:
            raise RecurringTransactionNotFoundError(cmd.rt_id)
        if rt.user_id != cmd.user_id:
            raise RecurringTransactionAccessForbiddenError()
        self._repo.delete(cmd.rt_id)
