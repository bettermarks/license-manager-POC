from typing import Optional

from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from licensing.model.base import Model


class Product(Model):
    eid: Mapped[str] = mapped_column(String(256), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(256), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(512))
    permissions: Mapped[JSON] = mapped_column(JSONB)


