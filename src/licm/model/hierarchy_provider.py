from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.orm import relationship

from licm.model.base import Base


class HierarchyProvider(Base):
    eid = Column(String(64), nullable=False, index=True)
    name = Column(String(64), nullable=False, index=True)
    description = Column(String(256))
    hierarchy_url = Column(String(256), nullable=False, index=True)

    hierarchy_levels = relationship("HierarchyLevel", back_populates="hierarchy_provider")
    products = relationship("Product", back_populates="hierarchy_provider")

    __table_args__ = (
        UniqueConstraint("eid", name="uix_hierarchy_provider"),
    )

