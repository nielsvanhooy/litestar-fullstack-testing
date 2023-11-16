"""CPE Business Product Controller Dependencies"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.cpe_business_product.models import CPEBusinessProduct
from app.domain.cpe_business_product.services import CPEBusinessProductService
from app.lib import log

__all__ = ["provides_cpe_business_service"]


logger = log.get_logger()

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


async def provides_cpe_business_service(db_session: AsyncSession) -> AsyncGenerator[CPEBusinessProductService, None]:
    """Construct repository and service objects for the request."""
    async with CPEBusinessProductService.new(session=db_session, statement=select(CPEBusinessProduct)) as service:
        try:
            yield service
        finally:
            ...
