from __future__ import annotations

from typing import TYPE_CHECKING

from app.lib.db import orm

if TYPE_CHECKING:
    from sqlalchemy.orm import Mapped

__all__ = ["CPEVendor"]


class CPEVendor(orm.TimestampedDatabaseModel):
    __tablename__ = "vendor"

    name: Mapped[str]
