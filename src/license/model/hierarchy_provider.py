from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from license.model.base import Model


class HierarchyProvider(Model):
    url: Mapped[str] = mapped_column(String(1024), index=True, unique=True)
    short_name: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(256), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(512))
