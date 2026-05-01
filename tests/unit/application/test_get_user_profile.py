import pytest
from uuid import UUID, uuid4

from application.dtos.user import GetUserProfileQuery, RegisterUserCommand
from application.use_cases.users.get_user_profile import GetUserProfileUseCase
from application.use_cases.users.register_user import RegisterUserUseCase
from domain.entities.user import User
from domain.exceptions.user import UserNotFoundError
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
def repo_with_user() -> tuple[InMemoryUserRepository, UUID]:
    repo = InMemoryUserRepository()
    hasher = FakePasswordHasher()
    result = RegisterUserUseCase(user_repo=repo, password_hasher=hasher).execute(
        RegisterUserCommand(
            first_name="Ana",
            last_name="Santos",
            email="ana@example.com",
            password="securepassword",
        )
    )
    return repo, result.user_id


class TestGetUserProfileUseCase:
    def test_returns_profile_for_existing_user(
        self, repo_with_user: tuple[InMemoryUserRepository, UUID]
    ) -> None:
        repo, user_id = repo_with_user
        uc = GetUserProfileUseCase(user_repo=repo)

        result = uc.execute(GetUserProfileQuery(user_id=user_id))

        assert result.email == "ana@example.com"
        assert result.full_name == "Ana Santos"
        assert result.is_admin is True
        assert result.user_id == user_id

    def test_raises_when_user_not_found(
        self, repo_with_user: tuple[InMemoryUserRepository, UUID]
    ) -> None:
        repo, _ = repo_with_user
        uc = GetUserProfileUseCase(user_repo=repo)

        with pytest.raises(UserNotFoundError):
            uc.execute(GetUserProfileQuery(user_id=uuid4()))

    def test_profile_contains_all_required_fields(
        self, repo_with_user: tuple[InMemoryUserRepository, UUID]
    ) -> None:
        repo, user_id = repo_with_user
        uc = GetUserProfileUseCase(user_repo=repo)

        result = uc.execute(GetUserProfileQuery(user_id=user_id))

        assert hasattr(result, "user_id")
        assert hasattr(result, "email")
        assert hasattr(result, "full_name")
        assert hasattr(result, "is_admin")
