"""DH10 — Retrieve the user-configured exchange rate for a given month."""

from uuid import UUID

from domain.entities.finance import UserExchangeRate
from domain.repositories.finance import UserExchangeRateRepository


class GetUserExchangeRateUseCase:
    def __init__(self, rate_repo: UserExchangeRateRepository) -> None:
        self._repo = rate_repo

    def execute(self, user_id: UUID, year: int, month: int) -> UserExchangeRate | None:
        return self._repo.get_by_user_and_period(user_id, year, month)

    def list(self, user_id: UUID) -> list[UserExchangeRate]:
        return self._repo.list_by_user(user_id)
