from uuid import UUID

from application.dtos.finance import TransactionListItemResponse
from domain.repositories.finance import TransactionRepository


class GetRecentTransactionsUseCase:
    """Return the latest N transactions for the user."""

    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self._repo = transaction_repo

    def execute(self, user_id: UUID, limit: int = 10) -> list[TransactionListItemResponse]:
        transactions = self._repo.list_by_user(user_id, limit=limit, offset=0)
        return [
            TransactionListItemResponse(
                transaction_id=tx.id,
                type=tx.type,
                amount=tx.amount,
                currency=tx.currency,
                exchange_rate=tx.exchange_rate,
                category=tx.category,
                category_id=tx.category_id,
                description=tx.description,
                is_base_salary=tx.is_base_salary,
                date=tx.date,
                notes=tx.notes,
                related_transaction_id=tx.related_transaction_id,
            )
            for tx in transactions
        ]
