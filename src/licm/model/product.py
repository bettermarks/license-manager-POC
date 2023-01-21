from sqlalchemy import Column, String

from licm.model.base import Base


class Product(Base):
    name = Column(String(64))
    description = Column(String(256))
