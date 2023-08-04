from __future__ import annotations

from typing import TYPE_CHECKING

from app.lib.db import orm

if TYPE_CHECKING:
    from sqlalchemy.orm import Mapped

__all__ = ["CPEBusinessProduct"]


class CPEBusinessProduct(orm.TimestampedDatabaseModel):
    __tablename__ = "business_product"  # type: ignore[assignment]

    key: Mapped[str]
    name: Mapped[str]
