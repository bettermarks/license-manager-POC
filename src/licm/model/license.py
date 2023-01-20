from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func

# please add this line for every model. We need that for the alembic migrations
Base = declarative_base()


class License(Base):
    __tablename__ = "license"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(64), nullable=False)
    description = Column(String(256))
    created_date = Column(DateTime, default=func.now(), nullable=False)
