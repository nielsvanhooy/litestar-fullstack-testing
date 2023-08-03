from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.lib.db import orm

if TYPE_CHECKING:
    from app.domain.cpe.models import CPEBusinessProduct, CPEVendor

__all__ = ["TSCMCheck"]


class TSCMCheck(orm.TimestampedDatabaseModel):
    key: Mapped[str] = mapped_column(String(50))
    # not sure if used anymore.
    regex: Mapped[str] = mapped_column(String(200), nullable=True, default="")
    python_code: Mapped[str] = mapped_column(Text, nullable=True, default="")
    remediation_commands: Mapped[str] = mapped_column(Text, nullable=True, default="")

    vendor: Mapped[list[CPEVendor]] = mapped_column(ForeignKey("vendor.id"))

    service: Mapped[list[CPEBusinessProduct]] = mapped_column(ForeignKey("business_product.id"))

    device_model: Mapped[str] = mapped_column(String(60), nullable=True, default="All")
    replaces_parent_check: Mapped[str] = mapped_column(String(100), nullable=True, default="None")
    has_child_checks: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
