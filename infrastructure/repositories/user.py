from uuid import UUID

from django.contrib.auth.hashers import check_password, make_password

from domain.entities.user import PasswordResetToken, User
from domain.repositories.user import PasswordHasher, PasswordResetTokenRepository, UserRepository
from infrastructure.django_app.models.user import PasswordResetTokenModel, UserModel


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

    def email_taken_by_other(self, email: str, exclude_user_id: UUID) -> bool:
        return UserModel.objects.filter(email=email).exclude(pk=exclude_user_id).exists()

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


class DjangoPasswordResetTokenRepository(PasswordResetTokenRepository):
    def save(self, token: PasswordResetToken) -> None:
        PasswordResetTokenModel.objects.create(
            token=token.token,
            user_id=token.user_id,
            used=token.used,
        )

    def get_by_token(self, token: UUID) -> PasswordResetToken | None:
        try:
            record = PasswordResetTokenModel.objects.get(pk=token)
            return PasswordResetToken(
                token=record.token,
                user_id=record.user_id,
                created_at=record.created_at,
                used=record.used,
            )
        except PasswordResetTokenModel.DoesNotExist:
            return None

    def mark_used(self, token: UUID) -> None:
        PasswordResetTokenModel.objects.filter(pk=token).update(used=True)
