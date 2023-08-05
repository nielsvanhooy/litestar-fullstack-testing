from __future__ import annotations

from app.lib.db import orm
from sqlalchemy.orm import Mapped

__all__ = ["CPEVendor"]


class CPEVendor(orm.TimestampedDatabaseModel):
    __tablename__ = "vendor"  # type: ignore[assignment]

    name: Mapped[str]
