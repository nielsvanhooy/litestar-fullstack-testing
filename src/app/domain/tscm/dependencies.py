"""TSCM Controller Dependencies"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.tscm.models import TSCMCheck, TSCMCheckResult
from app.domain.tscm.services import TscmCheckResultService, TscmService
from app.lib import log

__all__ = ["provides_tscm_service", "provides_tscm_check_results_service"]


logger = log.get_logger()

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


async def provides_tscm_service(db_session: AsyncSession) -> AsyncGenerator[TscmService, None]:
    """Construct repository and service objects for the request."""
    async with TscmService.new(session=db_session, statement=select(TSCMCheck)) as service:
        try:
            yield service
        finally:
            ...


async def provides_tscm_check_results_service(db_session: AsyncSession) -> AsyncGenerator[TscmCheckResultService, None]:
    """Construct repository and service objects for the request."""
    async with TscmCheckResultService.new(session=db_session, statement=select(TSCMCheckResult)) as service:
        try:
            yield service
        finally:
            ...
