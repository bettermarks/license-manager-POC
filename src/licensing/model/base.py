import datetime
import re
from typing import Optional

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import BIGINT, TIMESTAMP
from sqlalchemy.orm import declared_attr, Mapped, mapped_column


class Model(DeclarativeBase):
    """
    The common base class for all our models.
    Every model has these columns:
        id: the primary key
        created: some timestamp holding the creation date and time of the object
        updated: some timestamp holding the 'last updated' date and time for the object
    """

    @declared_attr
    def __tablename__(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()  # snake case ...

    # override the SQLAlchemy type annotation map
    type_annotation_map = {
        int: BIGINT,  # we want 64 bit ints for primary keys etc.
        datetime.datetime: TIMESTAMP(timezone=True)
    }

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    created: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True)
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.utcnow, index=True)
