from unittest.mock import MagicMock
from uuid import uuid4

from application.dtos.finance import AccountSummaryResponse, GetAccountsByUserQuery
from application.use_cases.finance.get_accounts_by_user import GetAccountsByUserUseCase
from domain.entities.finance import Account, AccountType, Currency


class TestGetAccountsByUserUseCase:
    def _make_uc(self) -> tuple[GetAccountsByUserUseCase, MagicMock]:
        repo = MagicMock()
        uc = GetAccountsByUserUseCase(account_repo=repo)
        return uc, repo

    def _make_account(self, user_id) -> Account:
        return Account(
            user_id=user_id,
            name="Mi Billetera",
            type=AccountType.WALLET,
            supported_currencies=[Currency.USD, Currency.USDT],
            default_currencies=[Currency.USD],
        )

    def test_returns_accounts_for_user(self) -> None:
        uc, repo = self._make_uc()
        user_id = uuid4()
        account = self._make_account(user_id)
        repo.list_by_user.return_value = [account]

        results = uc.execute(GetAccountsByUserQuery(user_id=user_id))

        assert len(results) == 1
        assert isinstance(results[0], AccountSummaryResponse)
        assert results[0].account_id == account.id
        assert results[0].name == "Mi Billetera"
        assert Currency.USD in results[0].supported_currencies
        assert Currency.USD in results[0].default_currencies
        repo.list_by_user.assert_called_once_with(user_id)

    def test_returns_empty_list_when_no_accounts(self) -> None:
        uc, repo = self._make_uc()
        repo.list_by_user.return_value = []

        results = uc.execute(GetAccountsByUserQuery(user_id=uuid4()))

        assert results == []

    def test_each_item_contains_only_summary_fields(self) -> None:
        uc, repo = self._make_uc()
        user_id = uuid4()
        repo.list_by_user.return_value = [self._make_account(user_id)]

        results = uc.execute(GetAccountsByUserQuery(user_id=user_id))
        item = results[0]

        assert hasattr(item, "account_id")
        assert hasattr(item, "name")
        assert hasattr(item, "type")
        assert hasattr(item, "supported_currencies")
        assert hasattr(item, "default_currencies")
