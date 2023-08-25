from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TCH003

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.lib.db import orm

if TYPE_CHECKING:
    import datetime

    from app.domain.cpe.models import CPE
    from app.domain.cpe_business_product.models import CPEBusinessProduct
    from app.domain.cpe_vendor.models import CPEVendor


__all__ = ["TSCMCheck", "TSCMCheckResult"]


class TSCMCheck(orm.TimestampedDatabaseModel):
    key: Mapped[str] = mapped_column(String(50))
    # not sure if used anymore.
    regex: Mapped[str] = mapped_column(String(200), nullable=True, default="")
    python_code: Mapped[str] = mapped_column(Text, nullable=True, default="")
    remediation_commands: Mapped[str] = mapped_column(Text, nullable=True, default="")
    device_model: Mapped[str] = mapped_column(String(60), nullable=True, default="All")
    replaces_parent_check: Mapped[str] = mapped_column(String(100), nullable=True, default="None")
    has_child_checks: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    # -----------
    # ORM Relationships
    # ------------
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id", ondelete="CASCADE"))
    service_id: Mapped[UUID] = mapped_column(ForeignKey("business_product.id", ondelete="CASCADE"))

    vendor: Mapped[CPEVendor] = relationship(lazy="selectin")
    service: Mapped[CPEBusinessProduct] = relationship(back_populates="tscm_checks", lazy="selectin")

    def __repr__(self) -> str:
        return f"TSCMCheck({self.key})"


class TSCMCheckResult(orm.TimestampedDatabaseModel):
    date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    is_compliant: Mapped[bool] = mapped_column(Boolean, default=False)
    # -----------
    # ORM Relationships
    # ------------
    cpe_id: Mapped[UUID] = mapped_column(ForeignKey("cpe.device_id", ondelete="CASCADE"))
    cpe: Mapped[CPE] = relationship(back_populates="tscm_check_results", lazy="select")

    def __repr__(self) -> str:
        return f"TSCMCheckResults({self.date})"
