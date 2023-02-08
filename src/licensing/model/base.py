import datetime
import re

from sqlalchemy import Column, DateTime, BigInteger
from sqlalchemy.orm import declarative_base, declared_attr


class Model:
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

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    created = Column(DateTime, default=datetime.datetime.now, index=True)
    updated = Column(DateTime, onupdate=datetime.datetime.now, index=True)


Model = declarative_base(cls=Model)
