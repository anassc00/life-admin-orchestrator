"""F10 — Create a new recurring transaction definition."""

import uuid
from decimal import Decimal
from uuid import UUID

from domain.entities.finance import Currency, Frequency, RecurringTransaction, TransactionType
from domain.exceptions.finance import AccountNotFoundError
from domain.repositories.finance import AccountRepository, RecurringTransactionRepository


class CreateRecurringTransactionCommand:
    def __init__(
        self,
        user_id: UUID,
        account_id: UUID,
        type: TransactionType,
        amount: Decimal,
        currency: Currency,
        description: str,
        frequency: Frequency,
        day: int,
        category_id: UUID | None = None,
    ) -> None:
        self.user_id = user_id
        self.account_id = account_id
        self.type = type
        self.amount = amount
        self.currency = currency
        self.description = description
        self.frequency = frequency
        self.day = day
        self.category_id = category_id


class CreateRecurringTransactionUseCase:
    def __init__(
        self,
        rt_repo: RecurringTransactionRepository,
        account_repo: AccountRepository,
    ) -> None:
        self._rt_repo = rt_repo
        self._account_repo = account_repo

    def execute(self, cmd: CreateRecurringTransactionCommand) -> RecurringTransaction:
        account = self._account_repo.get_by_id(cmd.account_id)
        if account is None or account.user_id != cmd.user_id:
            raise AccountNotFoundError(cmd.account_id)

        rt = RecurringTransaction(
            id=uuid.uuid4(),
            user_id=cmd.user_id,
            account_id=cmd.account_id,
            type=cmd.type,
            amount=cmd.amount,
            currency=cmd.currency,
            description=cmd.description,
            category_id=cmd.category_id,
            frequency=cmd.frequency,
            day=cmd.day,
        )
        self._rt_repo.save(rt)
        return rt
