from datetime import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from licensing.model.base import Model, int8
from licensing.model import license as license_model


class Seat(Model):
    # columns
    ref_license: Mapped[int8] = mapped_column(ForeignKey("license.id"), index=True)
    user_eid: Mapped[str] = mapped_column(String(256), index=True)
    occupied_at: Mapped[datetime] = mapped_column(index=True)
    released_at: Mapped[Optional[datetime]] = mapped_column(index=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(index=True)
    is_occupied: Mapped[bool] = mapped_column(index=True)

    # Relationships
    license: Mapped[license_model.License] = relationship("License")
