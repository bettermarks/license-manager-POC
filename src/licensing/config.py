from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_user: str
    database_password: str
    database_host: str
    database_port: str
    database_name: str

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()