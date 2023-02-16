from sqlalchemy import Column, String, BigInteger, ForeignKey, Date, Integer, orm, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID

from licensing.model.base import Model


class License(Model):
    ref_product = Column(BigInteger, ForeignKey('product.id'), nullable=False, index=True)
    ref_hierarchy_provider = Column(BigInteger, ForeignKey('hierarchy_provider.id'), nullable=False, index=True)
    purchaser_eid = Column(String(256), nullable=False, index=True)
    owner_type = Column(String(256), nullable=False, index=True)
    owner_level = Column(Integer, nullable=False, index=True)
    owner_eid = Column(String(256), nullable=False, index=True)
    license_uuid = Column(UUID(as_uuid=True), nullable=False, index=True)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=False)
    seats = Column(Integer, nullable=True)
    is_seats_shared = Column(Boolean, nullable=True, default=False)

    # Relationships
    product = orm.relationship("Product")
    hierarchy_provider = orm.relationship("HierarchyProvider")

    __table_args__ = (
        UniqueConstraint(
            "ref_product",
            "ref_hierarchy_provider",
            "purchaser_eid",
            "owner_type",
            "owner_eid",
            "valid_from",
            "valid_to"
        ),
    )
