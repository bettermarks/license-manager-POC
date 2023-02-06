from sqlalchemy import Column, String, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from licensing.model.base import Base


class Product(Base):
    eid = Column(String(64), nullable=False, index=True)
    name = Column(String(64))
    description = Column(String(256))

    __table_args__ = (
        UniqueConstraint("eid", name="uix_product"),
    )

