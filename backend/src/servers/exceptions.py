from src.exceptions import NotFoundException, UnauthorizedException


class ServerNotFoundException(NotFoundException):
    def __init__(self, message: str = "Monitored server not found"):
        super().__init__(message=message)


class ApiKeyRevokedException(UnauthorizedException):
    def __init__(self, message: str = "Agent API key has been revoked"):
        super().__init__(message=message)


class InvalidApiKeyException(UnauthorizedException):
    def __init__(self, message: str = "Invalid agent API key"):
        super().__init__(message=message)
