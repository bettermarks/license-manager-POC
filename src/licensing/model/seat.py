import datetime

from sqlalchemy import Column, String, BigInteger, ForeignKey, DateTime, orm, Boolean

from licensing.model.base import Model


class Seat(Model):
    ref_license = Column(BigInteger, ForeignKey('license.id'), nullable=False, index=True)
    user_eid = Column(String(256), nullable=False, index=True)
    occupied = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)
    released = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)
    last_login = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)
    is_occupied = Column(Boolean, default=False, index=True)

    # Relationships
    license = orm.relationship("License")
