from sqlalchemy import Column, String

from licensing.model.base import Model


class HierarchyProvider(Model):
    url = Column(String(1024), nullable=False, index=True, unique=True)
    short_name = Column(String(64), nullable=False, index=True)
    name = Column(String(256), nullable=False, index=True)
    description = Column(String(512))
