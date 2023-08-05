from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.lib.db import orm

__all__ = ["CPEBusinessProduct"]


class CPEBusinessProduct(orm.TimestampedDatabaseModel):
    __tablename__ = "business_product"  # type: ignore[assignment]

    key: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
