import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "mysql+aiomysql://root:root@localhost:3306/nodewatch"

    SECRET_KEY: str = "dev_secret_key_change_in_production_1234567890"
    RESET_SECRET_KEY: str = "nodewatch-reset-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    OFFLINE_TIMEOUT_SECONDS: int = 120
    ALERT_EVALUATION_INTERVAL_SECONDS: int = 30
    METRICS_RETENTION_DAYS: int = 30
    METRICS_CLEANUP_INTERVAL_SECONDS: int = 3600

    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
