from sqlalchemy import Column, String

from licensing.model.base import Model


class HierarchyProvider(Model):
    eid = Column(String(64), nullable=False, index=True, unique=True)
    name = Column(String(64), nullable=False, index=True)
    description = Column(String(256))
    hierarchy_url = Column(String(256), nullable=False, index=True)
