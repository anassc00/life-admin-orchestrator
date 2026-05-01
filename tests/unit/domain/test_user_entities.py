from uuid import UUID

import pytest

from domain.entities.user import User


class TestUserEntity:
    def test_user_created_with_admin_default(self) -> None:
        user = User(
            first_name="Ana",
            last_name="Santos",
            email="ana@example.com",
            hashed_password="hashed_secret",
        )
        assert user.is_admin is True
        assert isinstance(user.id, UUID)
        assert user.first_name == "Ana"
        assert user.last_name == "Santos"
        assert user.email == "ana@example.com"

    def test_user_is_frozen(self) -> None:
        user = User(
            first_name="Ana",
            last_name="Santos",
            email="ana@example.com",
            hashed_password="hashed_secret",
        )
        with pytest.raises(Exception):
            user.email = "other@example.com"  # type: ignore[misc]

    def test_user_email_stored_as_provided(self) -> None:
        email = "Test.User@Example.COM"
        user = User(
            first_name="Test",
            last_name="User",
            email=email,
            hashed_password="h",
        )
        assert user.email == email

    def test_two_users_with_same_data_get_different_ids(self) -> None:
        kwargs = dict(
            first_name="Ana",
            last_name="Santos",
            email="ana@example.com",
            hashed_password="h",
        )
        user_a = User(**kwargs)
        user_b = User(**kwargs)
        assert user_a.id != user_b.id

    def test_user_is_admin_can_be_overridden(self) -> None:
        user = User(
            first_name="Ana",
            last_name="Santos",
            email="ana@example.com",
            hashed_password="h",
            is_admin=False,
        )
        assert user.is_admin is False
