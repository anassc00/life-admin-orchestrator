from uuid import UUID


class UserAlreadyExistsError(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"A user with email '{email}' already exists.")
        self.email = email


class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid email or password.")


class UserNotFoundError(Exception):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"User with id '{user_id}' not found.")
        self.user_id = user_id


class EmailAlreadyTakenError(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email '{email}' is already in use by another account.")
        self.email = email


class InvalidCurrentPasswordError(Exception):
    def __init__(self) -> None:
        super().__init__("Current password is incorrect.")


class InvalidResetTokenError(Exception):
    def __init__(self) -> None:
        super().__init__("Reset token is invalid, expired, or already used.")


class AdminRequiredError(Exception):
    def __init__(self) -> None:
        super().__init__("This action requires administrator privileges.")
