from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4

from application.dtos.finance import (
    CurrencyExchangeRegisteredResponse,
    RegisterCurrencyExchangeCommand,
)
from domain.entities.finance import Transaction, TransactionType
from domain.exceptions.finance import (
    AccountAccessForbiddenError,
    AccountNotFoundError,
    InvalidExchangeMathError,
)
from domain.repositories.finance import AccountRepository, TransactionRepository


class RegisterCurrencyExchangeUseCase:
    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._account_repo = account_repo
        self._transaction_repo = transaction_repo

    def _round4(self, value: Decimal) -> Decimal:
        """Round a Decimal to 4 decimal places."""
        return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

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

        # Round all amounts to 4 decimal places before validation
        amount_out = self._round4(command.amount_out)
        amount_in = self._round4(command.amount_in)
        exchange_rate = self._round4(command.exchange_rate)

        # Math validation: check BOTH directions with 1% tolerance
        # Condition A: amount_in ≈ amount_out * exchange_rate
        # Condition B: amount_out ≈ amount_in * exchange_rate
        expected_a = amount_out * exchange_rate
        expected_b = amount_in * exchange_rate

        # Use relative tolerance of 1% (0.01)
        def is_close(a: Decimal, b: Decimal) -> bool:
            if a == 0 and b == 0:
                return True
            if a == 0 or b == 0:
                return False
            rel_diff = abs(a - b) / max(abs(a), abs(b))
            return rel_diff <= Decimal("0.01")

        if not (is_close(amount_in, expected_a) or is_close(amount_out, expected_b)):
            raise InvalidExchangeMathError()

        out_id = uuid4()
        in_id = uuid4()

        tx_out = Transaction(
            id=out_id,
            user_id=command.user_id,
            account_id=command.source_account_id,
            type=TransactionType.EXCHANGE_OUT,
            amount=amount_out,
            currency=command.currency_out,
            exchange_rate=exchange_rate,
            date=command.date,
            notes=command.notes,
            related_transaction_id=in_id,
        )
        tx_in = Transaction(
            id=in_id,
            user_id=command.user_id,
            account_id=command.dest_account_id,
            type=TransactionType.EXCHANGE_IN,
            amount=amount_in,
            currency=command.currency_in,
            exchange_rate=Decimal("1") / exchange_rate if exchange_rate > 0 else Decimal("0"),
            date=command.date,
            notes=command.notes,
            related_transaction_id=out_id,
        )

        self._transaction_repo.save_exchange_pair(tx_out, tx_in)

        return CurrencyExchangeRegisteredResponse(
            tx_out_id=out_id,
            tx_in_id=in_id,
            amount_out=amount_out,
            currency_out=command.currency_out,
            amount_in=amount_in,
            currency_in=command.currency_in,
        )
