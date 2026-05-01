from uuid import UUID

from django.contrib.auth.hashers import check_password, make_password

from domain.entities.user import User
from domain.repositories.user import PasswordHasher, UserRepository
from infrastructure.django_app.models.user import UserModel


class DjangoUserRepository(UserRepository):
    def get_by_email(self, email: str) -> User | None:
        try:
            record = UserModel.objects.get(email=email)
            return self._to_entity(record)
        except UserModel.DoesNotExist:
            return None

    def get_by_id(self, user_id: UUID) -> User | None:
        try:
            record = UserModel.objects.get(pk=user_id)
            return self._to_entity(record)
        except UserModel.DoesNotExist:
            return None

    def save(self, user: User) -> None:
        UserModel.objects.update_or_create(
            pk=user.id,
            defaults={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "hashed_password": user.hashed_password,
                "is_admin": user.is_admin,
            },
        )

    @staticmethod
    def _to_entity(record: UserModel) -> User:
        return User(
            id=record.id,
            first_name=record.first_name,
            last_name=record.last_name,
            email=record.email,
            hashed_password=record.hashed_password,
            is_admin=record.is_admin,
        )


class DjangoPasswordHasher(PasswordHasher):
    """Delegates to Django's PBKDF2 hasher (configured in settings)."""

    def hash(self, plain_password: str) -> str:
        return make_password(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return check_password(plain_password, hashed_password)
