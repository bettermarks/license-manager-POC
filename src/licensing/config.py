from functools import lru_cache
from pydantic import BaseSettings

from licensing.logging import LogLevel


class Settings(BaseSettings):
    # Generic settings
    log_level: str = LogLevel.DEBUG

    # DB settings
    database_user: str
    database_password: str
    database_host: str
    database_port: str
    database_name: str

    segment: str = ""

    apm_secret_token: str = ""
    apm_url: str = ""
    apm_enabled: str = "false"
    apm_transaction_sample_rate: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
