import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context

from licm.db import DATABASE_URL

# import the models here ...
from licm.model.base import Base
from licm.model import product, hierarchy_provider, hierarchy_level


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata              # RSC modified

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")

    # RSC 2023-01-19: We do apply the url dynamically for security reasons
    # No, we don't do this ... : url = config.get_main_option("sqlalchemy.url")
    # We will do that:
    url = DATABASE_URL

    context.configure(
       url=url,
       target_metadata=target_metadata,
       literal_binds=True,
       dialect_opts={"paramstyle": "named"},
   )

    with context.begin_transaction():
       context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # RSC 2023-01-19: We do apply the url dynamically for security reasons
    # for details, refer to
    # https://allan-simon.github.io/blog/posts/python-alembic-with-environment-variables/
    # So, we don't do this ... :
    # connectable = AsyncEngine(
    #    engine_from_config(
    #        config.get_section(config.config_ini_section),
    #        prefix="sqlalchemy.",
    #        poolclass=pool.NullPool,
    #        future=True,
    #    )
    # )    # Instead, we will do this:
    connectable = create_async_engine(DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
