from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.lib.db.orm import TimestampedDatabaseModel


class TSCMCheck(TimestampedDatabaseModel):
    key: Mapped[str] = mapped_column(String(50))
    # not sure if used anymore.
    regex: Mapped[str] = mapped_column(String(200), nullable=True, default="")
    python_code: Mapped[str] = mapped_column(Text)
