from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from application.dtos.finance import AccountRegisteredResponse, RegisterAccountCommand
from application.use_cases.finance.register_account import RegisterAccountUseCase
from domain.entities.finance import AccountType, Currency
from domain.exceptions.finance import AccountAlreadyExistsError


class TestRegisterAccountUseCase:
    def _make_uc(self) -> tuple[RegisterAccountUseCase, MagicMock]:
        repo = MagicMock()
        repo.exists_by_name_and_user.return_value = False
        uc = RegisterAccountUseCase(account_repo=repo)
        return uc, repo

    def test_registers_wallet_account_successfully(self) -> None:
        uc, repo = self._make_uc()
        user_id = uuid4()

        result = uc.execute(
            RegisterAccountCommand(
                user_id=user_id,
                name="Mi Billetera",
                type=AccountType.WALLET,
                supported_currencies=[Currency.USD, Currency.USDT],
                default_currencies=[Currency.USD],
            )
        )

        assert isinstance(result, AccountRegisteredResponse)
        assert result.name == "Mi Billetera"
        assert result.type == AccountType.WALLET
        repo.save.assert_called_once()

    def test_raises_if_account_name_already_exists_for_user(self) -> None:
        uc, repo = self._make_uc()
        repo.exists_by_name_and_user.return_value = True
        user_id = uuid4()

        with pytest.raises(AccountAlreadyExistsError):
            uc.execute(
                RegisterAccountCommand(
                    user_id=user_id,
                    name="Duplicada",
                    type=AccountType.CASH,
                    supported_currencies=[Currency.VES],
                    default_currencies=[Currency.VES],
                )
            )

    def test_different_users_can_have_same_account_name(self) -> None:
        uc, repo = self._make_uc()
        repo.exists_by_name_and_user.return_value = False

        result = uc.execute(
            RegisterAccountCommand(
                user_id=uuid4(),
                name="Caja Chica",
                type=AccountType.CASH,
                supported_currencies=[Currency.VES],
                default_currencies=[Currency.VES],
            )
        )

        assert result.name == "Caja Chica"
