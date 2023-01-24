import datetime
import re

from sqlalchemy import Column, DateTime, BigInteger
from sqlalchemy.orm import declarative_base, declared_attr


class Base:
    @declared_attr
    def __tablename__(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()   # snake case ...

    id = Column(BigInteger, primary_key=True, index=True)
    created = Column(DateTime, default=datetime.datetime.now, index=True)
    updated = Column(DateTime, onupdate=datetime.datetime.now, index=True)


Base = declarative_base(cls=Base)
