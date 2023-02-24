import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.engine import Connection

from licensing.db import DATABASE_DSN
from licensing.model.base import Model

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Model.metadata

target_metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)"
          "s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# you have to import all your models to support alembic 'autogenerate'
from licensing.model.hierarchy_provider import HierarchyProvider
from licensing.model.product import Product
from licensing.model.license import License
from licensing.model.seat import Seat


def run_migrations_offline() -> None:
    url = DATABASE_DSN
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# modified following https://pytest-alembic.readthedocs.io/en/latest/asyncio.html

def run_migrations_online():
    config_section = config.get_section(config.config_ini_section)
    url = DATABASE_DSN
    config_section["sqlalchemy.url"] = url
    connectable = context.config.attributes.get("connection", None)

    if connectable is None:
        connectable = AsyncEngine(
            engine_from_config(
                config_section,
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
                future=True,
            )
        )

    # Note, we decide whether to run asynchronously based on the kind of engine we're dealing with.
    if isinstance(connectable, AsyncEngine):
        asyncio.run(run_async_migrations(connectable))
    else:
        do_run_migrations(connectable)


# Then use their setup for async connection/running of the migration
async def run_async_migrations(connectable):
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


# But the outer layer still allows sychronous execution also.
run_migrations_online()
