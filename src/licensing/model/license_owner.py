from sqlalchemy import Column, String, BigInteger, ForeignKey, orm, UniqueConstraint

from licensing.model.base import Model


class LicenseOwner(Model):
    ref_hierarchy_provider = Column(BigInteger, ForeignKey('hierarchy_provider.id'), nullable=False, index=True)
    ref_license = Column(BigInteger, ForeignKey('license.id'), nullable=False, index=True)
    eid = Column(String(256), nullable=False, index=True)
    hierarchy_level = Column(String(256), nullable=False, index=True)

    # Relationships
    license = orm.relationship("License")
    hierarchy_provider = orm.relationship("HierarchyProvider")

    __table_args__ = (
        UniqueConstraint("ref_license", "ref_hierarchy_provider", "eid", "hierarchy_level"),
    )
