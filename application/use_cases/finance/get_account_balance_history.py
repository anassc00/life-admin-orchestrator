from datetime import date
from decimal import Decimal

from application.dtos.finance import (
    AccountBalanceHistoryItem,
    AccountBalanceHistoryResponse,
    GetAccountBalanceHistoryQuery,
)
from domain.entities.finance import TransactionType
from domain.exceptions.finance import AccountAccessForbiddenError, AccountNotFoundError
from domain.repositories.finance import AccountRepository, TransactionRepository


class GetAccountBalanceHistoryUseCase:
    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._account_repo = account_repo
        self._transaction_repo = transaction_repo

    def execute(self, query: GetAccountBalanceHistoryQuery) -> AccountBalanceHistoryResponse:
        account = self._account_repo.get_by_id(query.account_id)
        if account is None:
            raise AccountNotFoundError(query.account_id)

        if account.user_id != query.user_id:
            raise AccountAccessForbiddenError()

        today = date.today()
        items: list[AccountBalanceHistoryItem] = []

        for i in range(query.months - 1, -1, -1):
            # Walk backwards from current month
            month_offset = today.month - 1 - i
            year = today.year + month_offset // 12
            month = month_offset % 12 + 1

            transactions = self._transaction_repo.list_by_account(
                query.account_id, year=year, month=month
            )

            income = Decimal("0")
            expenses = Decimal("0")
            for tx in transactions:
                if tx.type in (TransactionType.INCOME, TransactionType.EXCHANGE_IN):
                    income += tx.amount
                elif tx.type in (TransactionType.EXPENSE, TransactionType.EXCHANGE_OUT):
                    expenses += tx.amount

            items.append(
                AccountBalanceHistoryItem(
                    year=year,
                    month=month,
                    income=income,
                    expenses=expenses,
                    net=income - expenses,
                )
            )

        return AccountBalanceHistoryResponse(account_id=query.account_id, items=items)
