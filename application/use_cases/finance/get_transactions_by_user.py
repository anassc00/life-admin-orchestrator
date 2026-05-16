from application.dtos.finance import GetTransactionsByUserQuery, TransactionListItemResponse
from domain.repositories.finance import TransactionRepository


class GetTransactionsByUserUseCase:
    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self._transaction_repo = transaction_repo

    def execute(self, query: GetTransactionsByUserQuery) -> list[TransactionListItemResponse]:
        transactions = self._transaction_repo.list_by_user(
            query.user_id,
            year=query.year,
            month=query.month,
            account_id=query.account_id,
            tx_type=query.tx_type,
            category_id=query.category_id,
            min_amount=query.min_amount,
            max_amount=query.max_amount,
            limit=query.limit,
            offset=query.offset,
        )
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
