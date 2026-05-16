from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user import PasswordResetToken, User


class UserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    def save(self, user: User) -> None: ...

    @abstractmethod
    def email_taken_by_other(self, email: str, exclude_user_id: UUID) -> bool:
        """Return True if email is already used by a different user."""
        ...


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain_password: str) -> str: ...

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool: ...


class PasswordResetTokenRepository(ABC):
    @abstractmethod
    def save(self, token: PasswordResetToken) -> None: ...

    @abstractmethod
    def get_by_token(self, token: UUID) -> PasswordResetToken | None: ...

    @abstractmethod
    def mark_used(self, token: UUID) -> None: ...
