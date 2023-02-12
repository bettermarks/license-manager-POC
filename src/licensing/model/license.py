from sqlalchemy import Column, String, BigInteger, ForeignKey, Date, Integer, orm

from licensing.model.base import Model


class License(Model):
    ref_product = Column(BigInteger, ForeignKey('product.id'), nullable=False, index=True)
    ref_hierarchy_provider = Column(BigInteger, ForeignKey('hierarchy_provider.id'), nullable=False, index=True)
    purchaser_eid = Column(String(256), nullable=False, index=True)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=False)
    seats = Column(Integer, nullable=True)

    # Relationships
    product = orm.relationship("Product")
    hierarchy_provider = orm.relationship("HierarchyProvider")
    owners = orm.relationship("LicenseOwner")
