from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.lib.db import orm

__all__ = ["CPEVendor"]


class CPEVendor(orm.TimestampedDatabaseModel):
    __tablename__ = "vendor"  # type: ignore[assignment]

    name: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
