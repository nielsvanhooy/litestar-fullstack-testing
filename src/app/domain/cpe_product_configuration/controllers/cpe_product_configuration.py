"""CPE Product Configuration Controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter

from app.domain import urls
from app.domain.accounts.guards import requires_superuser
from app.domain.cpe_product_configuration.dependencies import provides_product_config_service
from app.domain.cpe_product_configuration.dtos import CpeProductConfigurationDTO

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
        operation_id="ListCPEBusinessProducts",
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
