import os
import urllib
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from licm import config


def postgres_dsn(host: str, port: str, user: str, password: str, db_name: str, ssl: bool = False) -> str:
    return (
        f"postgresql+asyncpg://{user}:{urllib.parse.quote(password)}"
        f"@{host}:{port}"
        f"/{db_name}"
        f"{'?sslmode=require' if ssl else ''}"
    )


def get_var(var: str) -> str:
    return os.getenv(var) or getattr(config, var)


DATABASE_URL = postgres_dsn(
    get_var("DATABASE_HOST"),
    get_var("DATABASE_PORT"),
    get_var("DATABASE_USER"),
    get_var("DATABASE_PASSWORD"),
    get_var("DATABASE_NAME")
)

# SQLAlchemy
engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def get_session() -> AsyncSession:
    try:
        async with async_session_factory() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
