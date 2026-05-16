from datetime import date
from decimal import Decimal

from application.dtos.finance import EditTransactionCommand, TransactionEditedResponse
from domain.entities.finance import TransactionType
from domain.exceptions.finance import (
    AccountAccessForbiddenError,
    AccountNotFoundError,
    InvalidEditionCredentialsError,
    TransactionNotFoundError,
    UnauthorizedEditError,
)
from domain.repositories.finance import AccountRepository, TransactionRepository
from domain.repositories.user import PasswordHasher, UserRepository

_EXCHANGE_TYPES = {TransactionType.EXCHANGE_IN, TransactionType.EXCHANGE_OUT}


class EditTransactionUseCase:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
        account_repo: AccountRepository | None = None,
    ) -> None:
        self._transaction_repo = transaction_repo
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._account_repo = account_repo

    def execute(self, command: EditTransactionCommand) -> TransactionEditedResponse:
        tx = self._transaction_repo.get_by_id(command.transaction_id)
        if tx is None:
            raise TransactionNotFoundError(command.transaction_id)

        if tx.user_id != command.user_id:
            raise UnauthorizedEditError()

        user = self._user_repo.get_by_id(command.user_id)
        if user is None or not self._password_hasher.verify(command.password, user.hashed_password):
            raise InvalidEditionCredentialsError()

        # Validate the new account when provided
        if command.account_id is not None and self._account_repo is not None:
            account = self._account_repo.get_by_id(command.account_id)
            if account is None:
                raise AccountNotFoundError(command.account_id)
            if account.user_id != command.user_id:
                raise AccountAccessForbiddenError()

        update_fields: dict[str, object] = {"notes": command.notes}
        if command.account_id is not None:
            update_fields["account_id"] = command.account_id
        if command.amount is not None:
            update_fields["amount"] = command.amount
        if command.currency is not None:
            update_fields["currency"] = command.currency
        if command.date is not None:
            update_fields["date"] = (
                date.fromisoformat(command.date) if isinstance(command.date, str) else command.date
            )
        if command.description is not None:
            update_fields["description"] = command.description
        if command.exchange_rate is not None:
            update_fields["exchange_rate"] = command.exchange_rate

        updated_tx = tx.model_copy(update=update_fields)
        self._transaction_repo.save(updated_tx)

        # Cascade to the paired exchange transaction when amount or rate changes.
        # Currency is intentionally NOT cascaded: each side of an exchange pair
        # holds a different currency by design.
        amount_changed = command.amount is not None
        rate_changed = command.exchange_rate is not None
        if (
            tx.type in _EXCHANGE_TYPES
            and tx.related_transaction_id is not None
            and (amount_changed or rate_changed)
        ):
            related = self._transaction_repo.get_by_id(tx.related_transaction_id)
            if related is not None:
                new_amount = Decimal(str(updated_tx.amount))
                new_rate = Decimal(str(updated_tx.exchange_rate))

                if tx.type == TransactionType.EXCHANGE_OUT:
                    # OUT changed → recalculate IN amount: amount_in = amount_out * rate
                    related_updates: dict[str, object] = {
                        "amount": new_amount * new_rate,
                        "exchange_rate": new_rate,
                    }
                else:
                    # IN changed → recalculate OUT amount: amount_out = amount_in / rate
                    related_updates = {
                        "amount": new_amount / new_rate if new_rate else related.amount,
                        "exchange_rate": new_rate,
                    }
                self._transaction_repo.save(related.model_copy(update=related_updates))

        return TransactionEditedResponse(
            transaction_id=updated_tx.id,
            account_id=updated_tx.account_id,
            amount=updated_tx.amount,
            currency=updated_tx.currency,
            date=updated_tx.date,
            description=updated_tx.description,
            exchange_rate=updated_tx.exchange_rate,
            notes=updated_tx.notes,
        )
