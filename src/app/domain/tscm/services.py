from __future__ import annotations

from typing import Any

from app.lib.repository import SQLAlchemyAsyncRepository
from app.lib.service.sqlalchemy import SQLAlchemyAsyncRepositoryService

from .models import TSCMCheck

__all__ = ["TscmService", "TscmRepository"]

from app.domain.cpe_business_product.dependencies import provides_cpe_business_service
from app.domain.cpe_vendor.dependencies import provides_cpe_vendor_service


class TscmRepository(SQLAlchemyAsyncRepository[TSCMCheck]):
    """CPE Sqlalchemy Repository"""

    model_type = TSCMCheck


class TscmService(SQLAlchemyAsyncRepositoryService[TSCMCheck]):
    repository_type = TscmRepository

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: TscmRepository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

    async def create(self, data: TSCMCheck | dict[str, Any]) -> TSCMCheck:
        """Create a new TSCM check with relation service and vendor"""
        business_service = await anext(provides_cpe_business_service(db_session=self.repository.session))
        await business_service.get(data["service"])

        vendor_service = await anext(provides_cpe_vendor_service(db_session=self.repository.session))
        vendor_product = await vendor_service.get(data["vendor"])

        db_obj = await self.to_model(data, "create")
        db_obj.vendor.append(vendor_product)
        db_obj.service.append(business_service)
        return await super().create(db_obj)
