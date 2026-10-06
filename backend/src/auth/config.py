from src.config import settings


class AuthConfig:
    SECRET_KEY = settings.SECRET_KEY
    RESET_SECRET_KEY = settings.RESET_SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


auth_config = AuthConfig()
