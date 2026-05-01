from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import AccountUpdatedResponse, UpdateAccountCommand
from application.use_cases.finance.update_account import UpdateAccountUseCase
from domain.entities.finance import Account, AccountType, Currency
from domain.exceptions.finance import AccountAccessForbiddenError, AccountNotFoundError


class TestUpdateAccountUseCase:
    def _make_uc(self) -> tuple[UpdateAccountUseCase, MagicMock]:
        repo = MagicMock()
        uc = UpdateAccountUseCase(account_repo=repo)
        return uc, repo

    def _make_account(self, user_id) -> Account:
        return Account(
            user_id=user_id,
            name="Vieja",
            type=AccountType.CASH,
            supported_currencies=[Currency.VES],
            default_currencies=[Currency.VES],
        )

    def test_updates_account_name_and_currencies(self) -> None:
        uc, repo = self._make_uc()
        user_id = uuid4()
        account = self._make_account(user_id)
        repo.get_by_id.return_value = account

        result = uc.execute(
            UpdateAccountCommand(
                user_id=user_id,
                account_id=account.id,
                name="Nueva",
                type=AccountType.WALLET,
                supported_currencies=[Currency.USD, Currency.USDT],
                default_currencies=[Currency.USD],
            )
        )

        assert isinstance(result, AccountUpdatedResponse)
        assert result.name == "Nueva"
        assert result.type == AccountType.WALLET
        repo.save.assert_called_once()

    def test_raises_if_account_not_found(self) -> None:
        uc, repo = self._make_uc()
        repo.get_by_id.return_value = None

        with pytest.raises(AccountNotFoundError):
            uc.execute(
                UpdateAccountCommand(
                    user_id=uuid4(),
                    account_id=uuid4(),
                    name="X",
                    type=AccountType.BANK,
                    supported_currencies=[Currency.USD],
                    default_currencies=[Currency.USD],
                )
            )

    def test_raises_if_account_belongs_to_another_user(self) -> None:
        uc, repo = self._make_uc()
        owner_id = uuid4()
        account = self._make_account(owner_id)
        repo.get_by_id.return_value = account

        with pytest.raises(AccountAccessForbiddenError):
            uc.execute(
                UpdateAccountCommand(
                    user_id=uuid4(),  # different user
                    account_id=account.id,
                    name="Hack",
                    type=AccountType.CASH,
                    supported_currencies=[Currency.USD],
                    default_currencies=[Currency.USD],
                )
            )
