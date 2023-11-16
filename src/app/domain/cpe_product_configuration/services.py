from __future__ import annotations

from typing import Any

from app.domain.cpe_product_configuration.models import CPEProductConfiguration
from app.domain.cpe_vendor.dependencies import provides_cpe_vendor_service
from app.lib.repository import SQLAlchemyAsyncRepository
from app.lib.service import SQLAlchemyAsyncRepositoryService

__all__ = ["CPEProductConfigurationService", "CPEProductConfigurationRepository"]


class CPEProductConfigurationRepository(SQLAlchemyAsyncRepository[CPEProductConfiguration]):
    """CPE Product Configuration Sqlalchemy Repository"""

    model_type = CPEProductConfiguration


class CPEProductConfigurationService(SQLAlchemyAsyncRepositoryService[CPEProductConfiguration]):
    repository_type = CPEProductConfigurationRepository

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: CPEProductConfigurationRepository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

    async def create(self, data: CPEProductConfiguration | dict[str, Any]) -> CPEProductConfiguration:
        """Create a new CPE with relation service and vendor"""

        if isinstance(data, dict):
            data_vendor_id = data.get("vendor", None)

        vendor_service = await anext(provides_cpe_vendor_service(db_session=self.repository.session))
        vendor_product = await vendor_service.get(data_vendor_id, id_attribute="name")

        db_obj = await self.to_model(data, "create")
        db_obj.vendor = vendor_product

        return await super().create(db_obj)
