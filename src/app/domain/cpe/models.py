from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TCH003

from litestar.contrib.sqlalchemy.base import AuditColumns, CommonTableAttributes, orm_registry
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column, orm_insert_sentinel, relationship

if TYPE_CHECKING:
    from app.domain.cpe_business_product.models import CPEBusinessProduct
    from app.domain.cpe_vendor.models import CPEVendor

__all__ = ["CPE"]


class CPEPrimaryKey:
    """CPE Primary key field Mixin"""

    device_id: Mapped[str] = mapped_column(String(length=255), primary_key=True)

    @declared_attr
    def _sentinel(cls) -> Mapped[int]:
        return orm_insert_sentinel()


class CPEBase(CommonTableAttributes, CPEPrimaryKey, AuditColumns, DeclarativeBase):
    """Base for declarative models with device_id primary keys and audit columns."""

    registry = orm_registry


class CPE(CPEBase):
    routername: Mapped[str]
    os: Mapped[str]
    mgmt_ip: Mapped[str]
    sec_mgmt_ip: Mapped[str | None]

    # -----------
    # ORM Relationships
    # ------------
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id", ondelete="CASCADE"))
    service_id: Mapped[UUID] = mapped_column(ForeignKey("business_product.id", ondelete="CASCADE"))

    vendor: Mapped[CPEVendor] = relationship(lazy="selectin")
    service: Mapped[CPEBusinessProduct] = relationship(lazy="selectin")
