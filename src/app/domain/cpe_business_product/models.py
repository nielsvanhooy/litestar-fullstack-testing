from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.lib.db import orm

if TYPE_CHECKING:
    from app.domain.cpe.models import CPE
    from app.domain.tscm.models import TSCMCheck

__all__ = ["CPEBusinessProduct"]


class CPEBusinessProduct(orm.TimestampedDatabaseModel):
    __tablename__ = "business_product"  # type: ignore[assignment]

    key: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    tscm_checks: Mapped[list["TSCMCheck"]] = relationship(
        cascade="all, delete-orphan", back_populates="service", lazy="selectin"
    )
    cpes: Mapped[list["CPE"]] = relationship(back_populates="service", lazy="selectin")
