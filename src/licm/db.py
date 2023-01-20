import os
import urllib
import logging

from sqlalchemy import create_engine, MetaData

from databases import Database
from licm import config


def postgres_dsn(host, port, user, password, database, ssl=False):
    return (
        f"postgresql://{user}:{urllib.parse.quote(password)}"
        f"@{host}:{port}"
        f"/{database}"
        f"{'?sslmode=require' if ssl else ''}"
    )


def get_var(var):
    return os.getenv(var) or getattr(config, var)


DATABASE_URL = postgres_dsn(
    get_var("DATABASE_HOST"),
    get_var("DATABASE_PORT"),
    get_var("DATABASE_USER"),
    get_var("DATABASE_PASSWORD"),
    get_var("DATABASE_NAME")
)

print(f"DATABASE_URL = {DATABASE_URL}")

# SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()
# databases query builder
database = Database(DATABASE_URL)
