from application.dtos.finance import DeleteTransactionCommand, TransactionDeletedResponse
from domain.exceptions.finance import (
    InvalidEditionCredentialsError,
    TransactionNotFoundError,
    UnauthorizedEditError,
)
from domain.repositories.finance import TransactionRepository
from domain.repositories.user import PasswordHasher, UserRepository


class DeleteTransactionUseCase:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._transaction_repo = transaction_repo
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    def execute(self, command: DeleteTransactionCommand) -> TransactionDeletedResponse:
        tx = self._transaction_repo.get_by_id(command.transaction_id)
        if tx is None:
            raise TransactionNotFoundError(command.transaction_id)

        if tx.user_id != command.user_id:
            raise UnauthorizedEditError()

        user = self._user_repo.get_by_id(command.user_id)
        if user is None or not self._password_hasher.verify(command.password, user.hashed_password):
            raise InvalidEditionCredentialsError()

        related_id = tx.related_transaction_id
        if related_id is not None:
            self._transaction_repo.delete_pair(command.transaction_id, related_id)
        else:
            self._transaction_repo.delete(command.transaction_id)

        return TransactionDeletedResponse(
            transaction_id=command.transaction_id,
            related_transaction_id=related_id,
        )
