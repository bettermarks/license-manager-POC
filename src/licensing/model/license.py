from sqlalchemy import Column, String, BigInteger, ForeignKey, Date, Integer, orm
from sqlalchemy.dialects.postgresql import ARRAY

from licensing.model.base import Model


class License(Model):
    ref_product = Column(BigInteger, ForeignKey('product.id'), nullable=False, index=True)
    ref_hierarchy_provider = Column(BigInteger, ForeignKey('hierarchy_provider.id'), nullable=False, index=True)
    purchaser_eid = Column(String(256), nullable=False, index=True)
    owner_hierarchy_level = Column(String(256), nullable=False, index=True)
    owner_eids = Column(ARRAY(String(255)), nullable=False, index=True)
    start = Column(Date, nullable=False)
    end = Column(Date, nullable=False)
    seats = Column(Integer, nullable=True)

    # Relationships
    product = orm.relationship("Product")
    hierarchy_provider = orm.relationship("HierarchyProvider")
