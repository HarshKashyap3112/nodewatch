from src.exceptions import ConflictException, UnauthorizedException


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message=message)


class UserAlreadyExistsException(ConflictException):
    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(message=message)


class InvalidTokenException(UnauthorizedException):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message=message)


class UserNotFoundException(UnauthorizedException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message=message)
