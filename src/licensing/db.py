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
    settings.database_host,
    settings.database_port,
    settings.database_user,
    settings.database_password,
    settings.database_name
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
