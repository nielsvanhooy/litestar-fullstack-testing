from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TCH003

from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.lib.db import orm

if TYPE_CHECKING:
    from app.domain.cpe_vendor.models import CPEVendor


__all__ = ["CPEProductConfiguration"]


class CPEProductConfiguration(orm.TimestampedDatabaseModel):
    __tablename__ = "product_configuration"  # type: ignore[assignment]

    description: Mapped[str] = mapped_column(String(200))
    configuration_id: Mapped[str] = mapped_column(Integer, unique=True) # used to call this sap_id
    cpe_model: Mapped[str] = mapped_column(String(50))

    # -----------
    # ORM Relationships
    # ------------
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id", ondelete="CASCADE"))

    vendor: Mapped[CPEVendor] = relationship(lazy="selectin")
