from decimal import Decimal
from uuid import uuid4

from application.dtos.finance import (
    CurrencyExchangeRegisteredResponse,
    RegisterCurrencyExchangeCommand,
)
from domain.entities.finance import Transaction, TransactionType
from domain.exceptions.finance import AccountAccessForbiddenError, AccountNotFoundError
from domain.repositories.finance import AccountRepository, TransactionRepository


class RegisterCurrencyExchangeUseCase:
    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._account_repo = account_repo
        self._transaction_repo = transaction_repo

    def execute(
        self, command: RegisterCurrencyExchangeCommand
    ) -> CurrencyExchangeRegisteredResponse:
        source = self._account_repo.get_by_id(command.source_account_id)
        if source is None:
            raise AccountNotFoundError(command.source_account_id)

        if source.user_id != command.user_id:
            raise AccountAccessForbiddenError()

        dest = self._account_repo.get_by_id(command.dest_account_id)
        if dest is None:
            raise AccountNotFoundError(command.dest_account_id)

        if dest.user_id != command.user_id:
            raise AccountAccessForbiddenError()

        out_id = uuid4()
        in_id = uuid4()

        tx_out = Transaction(
            id=out_id,
            user_id=command.user_id,
            account_id=command.source_account_id,
            type=TransactionType.EXCHANGE_OUT,
            amount=command.amount_out,
            currency=command.currency_out,
            exchange_rate=command.exchange_rate,
            date=command.date,
            notes=command.notes,
            related_transaction_id=in_id,
        )
        tx_in = Transaction(
            id=in_id,
            user_id=command.user_id,
            account_id=command.dest_account_id,
            type=TransactionType.EXCHANGE_IN,
            amount=command.amount_in,
            currency=command.currency_in,
            exchange_rate=Decimal("1") / command.exchange_rate,
            date=command.date,
            notes=command.notes,
            related_transaction_id=out_id,
        )

        self._transaction_repo.save_exchange_pair(tx_out, tx_in)

        return CurrencyExchangeRegisteredResponse(
            tx_out_id=out_id,
            tx_in_id=in_id,
            amount_out=command.amount_out,
            currency_out=command.currency_out,
            amount_in=command.amount_in,
            currency_in=command.currency_in,
        )
