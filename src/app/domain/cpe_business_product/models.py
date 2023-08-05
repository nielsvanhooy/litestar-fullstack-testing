from __future__ import annotations

from app.lib.db import orm
from sqlalchemy.orm import Mapped

__all__ = ["CPEBusinessProduct"]


class CPEBusinessProduct(orm.TimestampedDatabaseModel):
    __tablename__ = "business_product"  # type: ignore[assignment]

    key: Mapped[str]
    name: Mapped[str]
