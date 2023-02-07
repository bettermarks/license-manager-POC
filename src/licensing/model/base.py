import re

from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel, Field


class Model(SQLModel):
    """
    The common base class for all our models.
    Every model has a column
    id: the primary key
    created: some timestamp holding the creation date and time of the object
    updated: some timestamp holding the 'last updated' date and time for the object
    """
    @declared_attr
    def __tablename__(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()   # snake case ...

    id: int = Field(default=None, primary_key=True)
    created: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)")
        }
    )

    updated: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"),
            "onupdate": text("current_timestamp(0)")
        }
    )
