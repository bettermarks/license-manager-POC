from sqlalchemy import Column, String

from licensing.model.base import Model


class HierarchyProvider(Model):
    eid = Column(String(256), nullable=False, index=True, unique=True)
    name = Column(String(256), nullable=False, index=True)
    description = Column(String(512))
    hierarchy_url = Column(String(1024), nullable=False, index=True)
