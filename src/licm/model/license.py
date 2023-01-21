from sqlalchemy import Column, String

from licm.model.base import Base


class License(Base):
    title = Column(String(64), nullable=False)
    description = Column(String(256))
