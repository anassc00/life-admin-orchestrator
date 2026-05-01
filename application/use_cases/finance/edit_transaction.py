from application.dtos.finance import EditTransactionCommand, TransactionEditedResponse
from domain.exceptions.finance import TransactionNotFoundError, UnauthorizedEditError
from domain.exceptions.user import InvalidCredentialsError
from domain.repositories.finance import TransactionRepository
from domain.repositories.user import PasswordHasher, UserRepository


class EditTransactionUseCase:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._transaction_repo = transaction_repo
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    def execute(self, command: EditTransactionCommand) -> TransactionEditedResponse:
        tx = self._transaction_repo.get_by_id(command.transaction_id)
        if tx is None:
            raise TransactionNotFoundError(command.transaction_id)

        if tx.user_id != command.user_id:
            raise UnauthorizedEditError()

        user = self._user_repo.get_by_id(command.user_id)
        if user is None or not self._password_hasher.verify(command.password, user.hashed_password):
            raise InvalidCredentialsError()

        updated_tx = tx.model_copy(update={"notes": command.notes})
        self._transaction_repo.save(updated_tx)

        return TransactionEditedResponse(
            transaction_id=updated_tx.id,
            notes=updated_tx.notes,
        )
