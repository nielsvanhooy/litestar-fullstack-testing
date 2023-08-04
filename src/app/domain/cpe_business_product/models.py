from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.lib.db import orm

__all__ = ["CPEBusinessProduct"]


class CPEBusinessProduct(orm.TimestampedDatabaseModel):
    __tablename__ = "business_product"

    key: Mapped[str]
    name: Mapped[str]
