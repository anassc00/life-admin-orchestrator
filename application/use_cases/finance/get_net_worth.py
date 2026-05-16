from decimal import Decimal
from uuid import UUID

from application.dtos.finance import NetWorthResponse, NetWorthBreakdownItem
from domain.entities.finance import AccountType
from domain.repositories.finance import AccountRepository


class GetNetWorthUseCase:
    """Sum all account balances converted to USD. Breakdown by account type."""

    def __init__(self, account_repo: AccountRepository) -> None:
        self._repo = account_repo

    def execute(self, user_id: UUID) -> NetWorthResponse:
        accounts = self._repo.list_by_user(user_id)
        total_usd = Decimal("0")
        by_type: dict[str, Decimal] = {
            AccountType.CASH.value: Decimal("0"),
            AccountType.BANK.value: Decimal("0"),
            AccountType.WALLET.value: Decimal("0"),
        }
        items = []

        for account in accounts:
            account_total_usd = Decimal("0")
            for currency, balance_str in account.current_balance.items():
                balance = Decimal(balance_str)
                # USD and USDT treated as 1:1; VES/MXN balances included as-is
                # (proper rate conversion is DH10 scope)
                if currency in ("USD", "USDT"):
                    account_total_usd += balance
                # Non-USD currencies: skip in net-worth (would need user-configured rate)

            total_usd += account_total_usd
            by_type[account.type.value] = by_type.get(account.type.value, Decimal("0")) + account_total_usd
            items.append(
                NetWorthBreakdownItem(
                    account_id=account.id,
                    name=account.name,
                    type=account.type,
                    balances=account.current_balance,
                    usd_equivalent=account_total_usd,
                )
            )

        return NetWorthResponse(
            total_usd=total_usd,
            cash_usd=by_type[AccountType.CASH.value],
            bank_usd=by_type[AccountType.BANK.value],
            wallet_usd=by_type[AccountType.WALLET.value],
            accounts=items,
        )
