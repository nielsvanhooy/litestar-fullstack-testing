from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.lib.db import orm

__all__ = ["CPEVendor"]


class CPEVendor(orm.TimestampedDatabaseModel):
    __tablename__ = "vendor"

    name: Mapped[str]
