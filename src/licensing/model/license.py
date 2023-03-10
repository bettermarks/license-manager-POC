import datetime
import uuid as uuid_module
from typing import Optional

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from licensing.model.base import Model, int8
from licensing.model import product as product_model
from licensing.model import hierarchy_provider as hierarchy_provider_model


class License(Model):
    uuid: Mapped[uuid_module.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    ref_product: Mapped[int8] = mapped_column(
        ForeignKey("product.id"), init=False, index=True
    )
    ref_hierarchy_provider: Mapped[int8] = mapped_column(
        ForeignKey("hierarchy_provider.id"), init=False, index=True
    )

    purchaser_eid: Mapped[str] = mapped_column(String(256), index=True)
    owner_type: Mapped[str] = mapped_column(String(256), index=True)
    owner_level: Mapped[int] = mapped_column(index=True)
    owner_eid: Mapped[str] = mapped_column(String(256), index=True)
    valid_from: Mapped[datetime.date] = mapped_column(index=True)
    valid_to: Mapped[datetime.date] = mapped_column(index=True)
    seats: Mapped[Optional[int]]
    is_seats_shared: Mapped[bool]

    # Relationships
    product: Mapped[product_model.Product] = relationship("Product", init=False)
    hierarchy_provider: Mapped[
        hierarchy_provider_model.HierarchyProvider
    ] = relationship("HierarchyProvider", init=False)

    __table_args__ = (
        UniqueConstraint(
            "ref_product",
            "ref_hierarchy_provider",
            "purchaser_eid",
            "owner_type",
            "owner_eid",
            "valid_from",
            "valid_to",
        ),
    )
