from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from licm.model.base import Base


class UserClassManagementProvider(Base):
    name = Column(String(64), nullable=False)
    description = Column(String(256))
    hierarchy_url = Column(String(256))

    hierarchy_levels = relationship("HierarchyLevel")
