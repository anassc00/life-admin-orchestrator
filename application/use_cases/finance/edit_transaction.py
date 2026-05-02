from application.dtos.finance import EditTransactionCommand, TransactionEditedResponse
from domain.exceptions.finance import (
    InvalidEditionCredentialsError,
    TransactionNotFoundError,
    UnauthorizedEditError,
)
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
            raise InvalidEditionCredentialsError()

        update_fields = {"notes": command.notes}
        if command.amount is not None:
            update_fields["amount"] = command.amount
        if command.date is not None:
            from datetime import date

            update_fields["date"] = (
                date.fromisoformat(command.date) if isinstance(command.date, str) else command.date
            )
        if command.description is not None:
            update_fields["description"] = command.description
        if command.exchange_rate is not None:
            update_fields["exchange_rate"] = command.exchange_rate

        updated_tx = tx.model_copy(update=update_fields)
        self._transaction_repo.save(updated_tx)

        return TransactionEditedResponse(
            transaction_id=updated_tx.id,
            amount=updated_tx.amount,
            date=updated_tx.date,
            description=updated_tx.description,
            exchange_rate=updated_tx.exchange_rate,
            notes=updated_tx.notes,
        )
