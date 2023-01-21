from sqlalchemy import Column, String, Integer, ForeignKey

from licm.model.base import Base


class HierarchyLevel(Base):
    ucm_provider = Column("ref_ucm_provider", Integer, ForeignKey("user_class_management_provider.id"))
    level = Column(Integer, nullable=False)
    name = Column(String(256))
    hierarchy_url = Column(String(256))


