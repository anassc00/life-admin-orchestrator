"""DH10 — Upsert the user-configured exchange rate for a given month."""

import uuid
from decimal import Decimal
from uuid import UUID

from domain.entities.finance import UserExchangeRate
from domain.repositories.finance import UserExchangeRateRepository


class SetUserExchangeRateCommand:
    def __init__(
        self,
        user_id: UUID,
        year: int,
        month: int,
        usd_ves: Decimal,
        usd_mxn: Decimal | None = None,
    ) -> None:
        self.user_id = user_id
        self.year = year
        self.month = month
        self.usd_ves = usd_ves
        self.usd_mxn = usd_mxn


class SetUserExchangeRateUseCase:
    def __init__(self, rate_repo: UserExchangeRateRepository) -> None:
        self._repo = rate_repo

    def execute(self, cmd: SetUserExchangeRateCommand) -> UserExchangeRate:
        existing = self._repo.get_by_user_and_period(cmd.user_id, cmd.year, cmd.month)
        if existing:
            rate = existing.model_copy(update={"usd_ves": cmd.usd_ves, "usd_mxn": cmd.usd_mxn})
        else:
            rate = UserExchangeRate(
                id=uuid.uuid4(),
                user_id=cmd.user_id,
                year=cmd.year,
                month=cmd.month,
                usd_ves=cmd.usd_ves,
                usd_mxn=cmd.usd_mxn,
            )
        self._repo.save(rate)
        return rate
