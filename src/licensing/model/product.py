from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from licensing.model.base import Model


class Product(Model):
    eid = Column(String(256), nullable=False, index=True, unique=True)
    name = Column(String(256))
    description = Column(String(512))
    permissions = Column(JSONB)


