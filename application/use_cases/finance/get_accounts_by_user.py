from application.dtos.finance import AccountSummaryResponse, GetAccountsByUserQuery
from domain.repositories.finance import AccountRepository


class GetAccountsByUserUseCase:
    def __init__(self, account_repo: AccountRepository) -> None:
        self._account_repo = account_repo

    def execute(self, query: GetAccountsByUserQuery) -> list[AccountSummaryResponse]:
        accounts = self._account_repo.list_by_user(query.user_id)
        return [
            AccountSummaryResponse(
                account_id=a.id,
                name=a.name,
                type=a.type,
                supported_currencies=a.supported_currencies,
                default_currencies=a.default_currencies,
            )
            for a in accounts
        ]
