from datetime import date

from application.dtos.finance import ReverseTransactionCommand, TransactionReversedResponse
from domain.entities.finance import Transaction, TransactionType
from domain.exceptions.finance import (
    InvalidEditionCredentialsError,
    TransactionNotFoundError,
    TransactionReversalNotSupportedError,
    UnauthorizedEditError,
)
from domain.repositories.finance import TransactionRepository
from domain.repositories.user import PasswordHasher, UserRepository

_REVERSIBLE_TYPES = {TransactionType.INCOME, TransactionType.EXPENSE}
_REVERSAL_MAP = {
    TransactionType.INCOME: TransactionType.EXPENSE,
    TransactionType.EXPENSE: TransactionType.INCOME,
}


class ReverseTransactionUseCase:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._transaction_repo = transaction_repo
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    def execute(self, command: ReverseTransactionCommand) -> TransactionReversedResponse:
        tx = self._transaction_repo.get_by_id(command.transaction_id)
        if tx is None:
            raise TransactionNotFoundError(command.transaction_id)

        if tx.user_id != command.user_id:
            raise UnauthorizedEditError()

        user = self._user_repo.get_by_id(command.user_id)
        if user is None or not self._password_hasher.verify(command.password, user.hashed_password):
            raise InvalidEditionCredentialsError()

        if tx.type not in _REVERSIBLE_TYPES:
            raise TransactionReversalNotSupportedError()

        reversal = Transaction(
            user_id=tx.user_id,
            account_id=tx.account_id,
            type=_REVERSAL_MAP[tx.type],
            amount=tx.amount,
            currency=tx.currency,
            exchange_rate=tx.exchange_rate,
            category=tx.category,
            category_id=tx.category_id,
            description=f"Reversal of {tx.id}",
            date=date.today(),
            notes=f"Reversal of transaction {tx.id}",
        )
        self._transaction_repo.save(reversal)

        return TransactionReversedResponse(
            original_transaction_id=tx.id,
            reversal_transaction_id=reversal.id,
            amount=reversal.amount,
            currency=reversal.currency,
            date=reversal.date,
        )
