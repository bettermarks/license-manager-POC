from sqlalchemy import Table, Column, Integer, String, DateTime, func

from licm.db import metadata

license = Table(
    "license",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(50)),
    Column("description", String(50)),
    Column("created_date", DateTime, default=func.now(), nullable=False),
)