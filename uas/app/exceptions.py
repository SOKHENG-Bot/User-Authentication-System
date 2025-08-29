class UserAlreadyExists(Exception):
    def __init__(self, message: str = "User with this email or username already exists."):
        super().__init__(message)


class InvalidPassword(Exception):
    def __init__(self, message: str = "Invalid password."):
        super().__init__(message)


class UserNotFound(Exception):
    def __init__(self, message: str = "User not found."):
        super().__init__(message)
