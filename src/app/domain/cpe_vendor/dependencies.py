"""CPE Vendor Controller Dependencies"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.cpe_vendor.models import CPEVendor
from app.domain.cpe_vendor.services import CPEVendorService
from app.lib import log

__all__ = ["provides_cpe_vendor_service"]


logger = log.get_logger()

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


async def provides_cpe_vendor_service(db_session: AsyncSession) -> AsyncGenerator[CPEVendorService, None]:
    """Construct repository and service objects for the request."""
    async with CPEVendorService.new(session=db_session, statement=select(CPEVendor)) as service:
        try:
            yield service
        finally:
            ...
