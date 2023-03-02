import datetime
import re
from typing import Optional
from typing_extensions import Annotated

from sqlalchemy import BIGINT, TIMESTAMP
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    Mapped,
    mapped_column,
    MappedAsDataclass,
)
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime


# my custom types ...
int8 = Annotated[
    int, mapped_column(type_=BIGINT)
]  # we want 64 bit unsigned ints for primary keys and foreign keys.


class UtcNow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(UtcNow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class Model(MappedAsDataclass, DeclarativeBase):
    """
    The common base class for all our models.
    Every model has these columns:
        id: the primary key
        created: some timestamp holding the creation date and time of the object
        updated: some timestamp holding the 'last updated' date and time for the object
    """

    @declared_attr
    def __tablename__(cls):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()  # snake case ...

    # override the SQLAlchemy type annotation map
    type_annotation_map = {datetime.datetime: TIMESTAMP(timezone=True)}

    id: Mapped[int8] = mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )
    created: Mapped[Optional[datetime.datetime]] = mapped_column(
        init=False, server_default=UtcNow(), index=True
    )
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(
        init=False, onupdate=datetime.datetime.utcnow
    )
