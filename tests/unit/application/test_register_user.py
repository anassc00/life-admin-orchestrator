import pytest

from application.dtos.user import RegisterUserCommand
from application.use_cases.users.register_user import RegisterUserUseCase
from domain.entities.user import User
from domain.exceptions.user import UserAlreadyExistsError
from domain.repositories.user import PasswordHasher, UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._store: dict[str, User] = {}

    def get_by_email(self, email: str) -> User | None:
        return self._store.get(email)

    def save(self, user: User) -> None:
        self._store[user.email] = user


class FakePasswordHasher(PasswordHasher):
    def hash(self, plain_password: str) -> str:
        return f"hashed:{plain_password}"

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{plain_password}"


@pytest.fixture
def repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


class TestRegisterUserUseCase:
    def test_registers_user_successfully(
        self, repo: InMemoryUserRepository, hasher: FakePasswordHasher
    ) -> None:
        uc = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)
        command = RegisterUserCommand(
            first_name="Ana",
            last_name="Santos",
            email="ana@example.com",
            password="securepassword",
        )

        response = uc.execute(command)

        assert response.email == "ana@example.com"
        assert response.full_name == "Ana Santos"
        assert response.is_admin is True
        assert repo.get_by_email("ana@example.com") is not None

    def test_password_is_hashed_not_stored_in_plain(
        self, repo: InMemoryUserRepository, hasher: FakePasswordHasher
    ) -> None:
        uc = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)
        uc.execute(
            RegisterUserCommand(
                first_name="Ana",
                last_name="Santos",
                email="ana@example.com",
                password="securepassword",
            )
        )

        persisted = repo.get_by_email("ana@example.com")
        assert persisted is not None
        assert persisted.hashed_password != "securepassword"
        assert persisted.hashed_password == "hashed:securepassword"

    def test_raises_when_email_already_exists(
        self, repo: InMemoryUserRepository, hasher: FakePasswordHasher
    ) -> None:
        uc = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)
        command = RegisterUserCommand(
            first_name="Ana",
            last_name="Santos",
            email="ana@example.com",
            password="securepassword",
        )
        uc.execute(command)

        with pytest.raises(UserAlreadyExistsError):
            uc.execute(command)
