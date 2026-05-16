from application.dtos.finance import DeleteSavingsDepositCommand
from domain.exceptions.finance import (
    SavingsDepositAccessForbiddenError,
    SavingsDepositNotFoundError,
)
from domain.repositories.finance import SavingsDepositRepository


class DeleteSavingsDepositUseCase:
    """Delete a savings deposit record.

    Verifies ownership before deleting so one user cannot remove
    another user's deposit.
    """

    def __init__(self, savings_deposit_repo: SavingsDepositRepository) -> None:
        self._repo = savings_deposit_repo

    def execute(self, cmd: DeleteSavingsDepositCommand) -> None:
        deposit = self._repo.get_by_id(cmd.deposit_id)
        if deposit is None:
            raise SavingsDepositNotFoundError(cmd.deposit_id)
        if deposit.user_id != cmd.user_id:
            raise SavingsDepositAccessForbiddenError()
        self._repo.delete(cmd.deposit_id)
