from sqlalchemy import Column, String

from licensing.model.base import Model


class Product(Model):
    eid = Column(String(64), nullable=False, index=True, unique=True)
    name = Column(String(64))
    description = Column(String(256))


