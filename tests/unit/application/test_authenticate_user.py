import pytest
from uuid import UUID

from application.dtos.user import AuthenticateUserCommand, RegisterUserCommand
from application.use_cases.users.authenticate_user import AuthenticateUserUseCase
from application.use_cases.users.register_user import RegisterUserUseCase
from domain.entities.user import User
from domain.exceptions.user import InvalidCredentialsError
from domain.repositories.user import PasswordHasher, UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._by_email: dict[str, User] = {}
        self._by_id: dict[UUID, User] = {}

    def get_by_email(self, email: str) -> User | None:
        return self._by_email.get(email)

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._by_id.get(user_id)

    def save(self, user: User) -> None:
        self._by_email[user.email] = user
        self._by_id[user.id] = user


class FakePasswordHasher(PasswordHasher):
    def hash(self, plain_password: str) -> str:
        return f"hashed:{plain_password}"

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{plain_password}"


@pytest.fixture
def populated_repo() -> tuple[InMemoryUserRepository, FakePasswordHasher]:
    repo = InMemoryUserRepository()
    hasher = FakePasswordHasher()
    RegisterUserUseCase(user_repo=repo, password_hasher=hasher).execute(
        RegisterUserCommand(
            first_name="Ana",
            last_name="Santos",
            email="ana@example.com",
            password="securepassword",
        )
    )
    return repo, hasher


class TestAuthenticateUserUseCase:
    def test_authenticates_user_successfully(
        self, populated_repo: tuple[InMemoryUserRepository, FakePasswordHasher]
    ) -> None:
        repo, hasher = populated_repo
        uc = AuthenticateUserUseCase(user_repo=repo, password_hasher=hasher)

        response = uc.execute(
            AuthenticateUserCommand(email="ana@example.com", password="securepassword")
        )

        assert response.email == "ana@example.com"
        assert response.full_name == "Ana Santos"
        assert response.is_admin is True

    def test_raises_when_user_not_found(
        self, populated_repo: tuple[InMemoryUserRepository, FakePasswordHasher]
    ) -> None:
        repo, hasher = populated_repo
        uc = AuthenticateUserUseCase(user_repo=repo, password_hasher=hasher)

        with pytest.raises(InvalidCredentialsError):
            uc.execute(
                AuthenticateUserCommand(
                    email="nonexistent@example.com",
                    password="securepassword",
                )
            )

    def test_raises_when_password_invalid(
        self, populated_repo: tuple[InMemoryUserRepository, FakePasswordHasher]
    ) -> None:
        repo, hasher = populated_repo
        uc = AuthenticateUserUseCase(user_repo=repo, password_hasher=hasher)

        with pytest.raises(InvalidCredentialsError):
            uc.execute(
                AuthenticateUserCommand(
                    email="ana@example.com",
                    password="wrongpassword",
                )
            )

    def test_does_not_reveal_whether_user_exists(
        self, populated_repo: tuple[InMemoryUserRepository, FakePasswordHasher]
    ) -> None:
        """Both 'user not found' and 'wrong password' raise the same exception."""
        repo, hasher = populated_repo
        uc = AuthenticateUserUseCase(user_repo=repo, password_hasher=hasher)

        exc_no_user = None
        exc_bad_pass = None

        with pytest.raises(InvalidCredentialsError) as exc_info:
            uc.execute(AuthenticateUserCommand(email="ghost@example.com", password="x"))
        exc_no_user = type(exc_info.value)

        with pytest.raises(InvalidCredentialsError) as exc_info:
            uc.execute(AuthenticateUserCommand(email="ana@example.com", password="wrong"))
        exc_bad_pass = type(exc_info.value)

        assert exc_no_user is exc_bad_pass
