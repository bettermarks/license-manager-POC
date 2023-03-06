import urllib
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from licensing import settings


def postgres_dsn(
    host: str, port: str, user: str, password: str, db_name: str, ssl: bool = False
) -> str:
    return (
        f"postgresql+asyncpg://{user}:{urllib.parse.quote(password)}"
        f"@{host}:{port}"
        f"/{db_name}"
        f"{'?sslmode=require' if ssl else ''}"
    )


DATABASE_DSN = postgres_dsn(
    settings.database_host,
    settings.database_port,
    settings.database_user,
    settings.database_password,
    settings.database_name,
)

# SQLAlchemy session
# TODO True if settings.LOGLEVEL == logging.DEBUG else False   # lots of logging ...
async_engine = create_async_engine(DATABASE_DSN, echo=False)  #
async_session_factory = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)


async def async_session() -> AsyncSession:
    """
    This is the session generator usually injected using FastAPI 'Depends'
    function ...
    """
    try:
        async with async_session_factory() as session:
            yield session
    except Exception as ex:
        await session.rollback()
        raise ex
    finally:
        await session.close()


# ... but we sometimes want a context manager to use the DB session with 'with'
async_session_context = asynccontextmanager(async_session)
