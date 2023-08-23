"""CPE Product Configuration Controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter

from app.domain import urls
from app.domain.accounts.guards import requires_superuser
from app.domain.cpe_product_configuration.dependencies import provides_product_config_service
from app.domain.cpe_product_configuration.dtos import (
    CpeProductConfigurationDTO,
    CPEProductConfigurationUpdateDTO,
    CreateCPEProductConfiguration,
    CreateCpeProductConfigurationDTO,
    UpdateCPEProductConfiguration,
)
from app.lib import log

__all__ = ["CpeProductConfigurationController"]


if TYPE_CHECKING:
    from litestar.contrib.repository.filters import FilterTypes
    from litestar.dto import DTOData
    from litestar.pagination import OffsetPagination

    from app.domain.cpe_product_configuration.models import CPEProductConfiguration
    from app.domain.cpe_product_configuration.services import CPEProductConfigurationService


logger = log.get_logger()


class CpeProductConfigurationController(Controller):
    """CPE Product Configueration Controller."""

    tags = ["CPE Product Configuration"]
    guards = [requires_superuser]
    dependencies = {"cpes_product_config_service": Provide(provides_product_config_service)}
    return_dto = CpeProductConfigurationDTO

    @get(
        operation_id="ListCPEProductConfigurations",
        name="cpeproductconfigurations:list",
        summary="List CPE Product Configurations",
        cache_control=None,
        description="Retrieve the cpe product configurations",
        path=urls.CPE_PROD_CONFIGS,
    )
    async def list_cpe_product_configurations(
        self,
        cpes_product_config_service: CPEProductConfigurationService,
        filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> OffsetPagination[CPEProductConfiguration]:
        """List business products."""
        results, total = await cpes_product_config_service.list_and_count(*filters)
        return cpes_product_config_service.to_dto(results, total, *filters)

    @get(
        operation_id="GetCPEProductConfiguration",
        name="cpeproductconfigurations:get",
        path=urls.CPE_PROD_CONFIGS_DETAIL,
        summary="Retrieve the details of a product configuration",
    )
    async def get_cpe_product_configurations(
        self,
        cpes_product_config_service: CPEProductConfigurationService,
        product_configuration_id: str = Parameter(
            title="product configuration id", description="The product configuration to retrieve"
        ),
    ) -> CPEProductConfiguration:
        """Get a Product Configuration"""
        db_obj = await cpes_product_config_service.get(product_configuration_id)
        return cpes_product_config_service.to_dto(db_obj)

    @post(
        operation_id="CreateCPEProductConfiguration",
        name="cpeproductconfigurations:create",
        summary="Create a new Product Configuration",
        cache_control=None,
        description="A Product Configuration",
        path=urls.CPE_PROD_CONFIGS_CREATE,
        dto=CreateCpeProductConfigurationDTO,
    )
    async def create_cpe_product_configurations(
        self,
        cpes_product_config_service: CPEProductConfigurationService,
        data: DTOData[CreateCPEProductConfiguration],
    ) -> CPEProductConfiguration:
        """Create a Cpe Product Configuration"""
        obj = data.create_instance()
        db_obj = await cpes_product_config_service.create(obj.__dict__)
        return cpes_product_config_service.to_dto(db_obj)

    @patch(
        operation_id="UpdateCPEProductConfiguration",
        name="cpeproductconfigurations:update",
        summary="Update CPE Product Configuration",
        path=urls.CPE_PROD_CONFIGS_UPDATE,
        dto=CPEProductConfigurationUpdateDTO,
    )
    async def update_cpe_product_configurations(
        self,
        data: DTOData[UpdateCPEProductConfiguration],
        cpes_product_config_service: CPEProductConfigurationService,
        product_configuration_id: str = Parameter(
            title="product configuration id", description="The product configuration to Update"
        ),
    ) -> CPEProductConfiguration:
        """Update a CPE Product Configuration"""
        obj = data.create_instance()
        db_obj = await cpes_product_config_service.update(product_configuration_id, obj.__dict__)
        return cpes_product_config_service.to_dto(db_obj)

    @delete(
        operation_id="DeleteCPEProductConfiguration",
        name="cpeproductconfigurations:delete",
        path=urls.CPE_PROD_CONFIGS_DELETE,
        summary="Remove CPE",
        cache_control=None,
        description="Removes a CPE Product configuration and all associated data from the system.",
        return_dto=None,
    )
    async def delete_cpe(
        self,
        cpes_product_config_service: CPEProductConfigurationService,
        product_configuration_id: str = Parameter(
            title="product configuration id", description="The product configuration to Delete"
        ),
    ) -> None:
        """Delete a cpe from the system."""
        _ = await cpes_product_config_service.delete(product_configuration_id)
