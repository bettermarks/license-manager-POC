from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_user: str = "licm"
    database_password: str = "licm"
    database_host: str = "postgres"
    database_port: str = "5432"
    database_name: str = "licm"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()