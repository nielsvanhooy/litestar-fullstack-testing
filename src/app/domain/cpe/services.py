from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.domain.cpe_business_product.dependencies import provides_cpe_business_service
from app.domain.cpe_product_configuration.dependencies import provides_product_config_service
from app.domain.cpe_vendor.dependencies import provides_cpe_vendor_service
from app.lib.repository import SQLAlchemyAsyncRepository
from app.lib.service.sqlalchemy import SQLAlchemyAsyncRepositoryService

from .models import CPE

__all__ = ["CPEService", "CpeRepository"]


class CpeRepository(SQLAlchemyAsyncRepository[CPE]):
    """CPE Sqlalchemy Repository"""

    model_type = CPE
    id_attribute = "device_id"

    async def get_cpes_to_ping(self) -> dict[str, Any]:
        statement = select(CPE.device_id, CPE.mgmt_ip)
        db_data = await self._execute(statement)

        return {result[1]: {"device_id": result[0], "mgmt_ip": result[1]} for result in db_data}


class CPEService(SQLAlchemyAsyncRepositoryService[CPE]):
    repository_type = CpeRepository

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: CpeRepository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

    async def create(self, data: CPE | dict[str, Any]) -> CPE:
        """Create a new CPE with relation service and vendor"""

        if isinstance(data, dict):
            data_business_product_id = data.get("business_service", None)
            data_vendor_id = data.get("vendor", None)
            data_prd_config_id = data.get("product_configuration", None)

        business_service = await anext(provides_cpe_business_service(db_session=self.repository.session))
        business_product = await business_service.get(data_business_product_id, id_attribute="name")

        vendor_service = await anext(provides_cpe_vendor_service(db_session=self.repository.session))
        vendor_product = await vendor_service.get(data_vendor_id, id_attribute="name")

        prd_config_service = await anext(provides_product_config_service(db_session=self.repository.session))
        prd_config = await prd_config_service.get(data_prd_config_id, id_attribute="configuration_id")

        db_obj = await self.to_model(data, "create")
        db_obj.vendor = vendor_product
        db_obj.service = business_product
        db_obj.product_configuration = prd_config

        return await super().create(db_obj)

    async def get_cpes_to_ping(self) -> dict[str, Any]:
        return await self.repository.get_cpes_to_ping()
