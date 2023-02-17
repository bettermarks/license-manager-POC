import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from licensing.model.base import Model


class Seat(Model):
    ref_license: Mapped[int] = mapped_column(ForeignKey('license.id'), index=True)
    user_eid: Mapped[str] = mapped_column(String(256), index=True)
    occupied_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, index=True)
    released_at: Mapped[Optional[datetime.datetime]] = mapped_column(index=True)
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(index=True)
    is_occupied: Mapped[bool]

    # Relationships
    license = relationship("License")
