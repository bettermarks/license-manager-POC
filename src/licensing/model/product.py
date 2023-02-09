from sqlalchemy import Column, String, orm

from licensing.model.base import Model


class Product(Model):
    eid = Column(String(256), nullable=False, index=True, unique=True)
    name = Column(String(256))
    description = Column(String(512))
    # licenses = orm.relationship('License', backref='product')

