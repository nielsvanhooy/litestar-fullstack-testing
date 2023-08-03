from litestar.contrib.sqlalchemy.base import AuditColumns, CommonTableAttributes, orm_registry
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column, orm_insert_sentinel
from app.lib.db.orm import TimestampedDatabaseModel

__all__ = ["CPE"]


class CPEPrimaryKey:
    """CPE Primary key field Mixin"""

    device_id: Mapped[str] = mapped_column(String(length=255), primary_key=True)

    @declared_attr
    def _sentinel(cls) -> Mapped[int]:
        return orm_insert_sentinel()


class CPEBase(CommonTableAttributes, CPEPrimaryKey, AuditColumns, DeclarativeBase):
    """Base for declarative models with device_id primary keys and audit columns."""

    registry = orm_registry


class CPE(CPEBase):
    routername: Mapped[str]
    os: Mapped[str]
    mgmt_ip: Mapped[str]
    sec_mgmt_ip: Mapped[str | None]


class CPEVendor(TimestampedDatabaseModel):
    name: Mapped[str]


class CPEService(TimestampedDatabaseModel):
    key: Mapped[str]
    name: Mapped[str]
