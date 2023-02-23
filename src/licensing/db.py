import sys
import urllib
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from licensing.config import settings


def postgres_dsn(host: str, port: str, user: str, password: str, db_name: str, ssl: bool = False) -> str:
    return (
        f"postgresql+asyncpg://{user}:{urllib.parse.quote(password)}"
        f"@{host}:{port}"
        f"/{db_name}"
        f"{'?sslmode=require' if ssl else ''}"
    )


DATABASE_URL = postgres_dsn(
    settings.DATABASE_HOST,
    settings.DATABASE_PORT,
    settings.DATABASE_USER,
    settings.DATABASE_PASSWORD,
    settings.DATABASE_NAME
)

# SQLAlchemy session
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False  # TODO True if settings.LOGLEVEL == logging.DEBUG else False   # lots of logging ...
)
async_session_factory = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session() -> AsyncSession:
    """This is the session generator usually injected using FastAPI 'Depends' function"""
    try:
        async with async_session_factory() as session:
            yield session
    except Exception as ex:
        await session.rollback()
        raise ex
    finally:
        await session.close()


# We sometimes want a context manager to use the DB session with 'with'
get_async_session_context = asynccontextmanager(get_async_session)
