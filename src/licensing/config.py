from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Generic settings
    api_version_prefix: str = "/api/v1"
    debug: bool = False
    project_name: str = "License Manager POC"
    version: str = "0.0.1"
    description: str = "A generic license managing application"

    # DB settings
    database_user: str
    database_password: str
    database_host: str
    database_port: str
    database_name: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
