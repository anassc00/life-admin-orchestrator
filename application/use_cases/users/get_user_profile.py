from application.dtos.user import GetUserProfileQuery, UserProfileResponse
from domain.exceptions.user import UserNotFoundError
from domain.repositories.user import UserRepository


class GetUserProfileUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    def execute(self, query: GetUserProfileQuery) -> UserProfileResponse:
        user = self._repo.get_by_id(query.user_id)
        if user is None:
            raise UserNotFoundError(query.user_id)

        return UserProfileResponse(
            user_id=user.id,
            email=user.email,
            full_name=f"{user.first_name} {user.last_name}",
            is_admin=user.is_admin,
        )
