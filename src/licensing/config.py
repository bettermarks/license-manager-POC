from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Generic settings
    DEBUG: bool = False

    # DB settings
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_NAME: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
