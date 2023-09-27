"""CPE Product Configuration Controller Dependencies"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.cpe_product_configuration.models import CPEProductConfiguration
from app.domain.cpe_product_configuration.services import CPEProductConfigurationService
from app.lib import log

__all__ = ["provides_product_config_service"]


logger = log.get_logger()

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


async def provides_product_config_service(
    db_session: AsyncSession,
) -> AsyncGenerator[CPEProductConfigurationService, None]:
    """Construct repository and service objects for the request."""
    async with CPEProductConfigurationService.new(
        session=db_session,
        statement=select(CPEProductConfiguration),
    ) as service:
        try:
            yield service
        finally:
            ...
