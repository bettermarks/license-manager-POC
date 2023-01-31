from sqlalchemy import Column, String, Integer, ForeignKey, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship

from licensing.model.base import Base


class HierarchyLevel(Base):
    level = Column(Integer, nullable=False, index=True)
    name = Column(String(256), nullable=False, index=True)
    ref_hierarchy_provider = Column(
        "ref_hierarchy_provider", BigInteger, ForeignKey("hierarchy_provider.id"), nullable=False, index=True
    )
    hierarchy_provider = relationship("HierarchyProvider", back_populates="hierarchy_levels")

    __table_args__ = (
        UniqueConstraint("ref_hierarchy_provider", "level", name="uix_hierarchy_level"),
    )

