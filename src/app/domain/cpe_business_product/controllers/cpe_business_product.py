"""CPE Business Service Controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter

from app.domain import urls
from app.domain.accounts.guards import requires_superuser
from app.domain.cpe_business_product.dependencies import provides_cpe_business_service
from app.domain.cpe_business_product.dtos import (
    CpeBusinessDTO,
    CPEBusinessProductUpdateDTO,
    CreateCPEBusinessProduct,
    CreateCpeBusinessProductDTO,
    UpdateCPEBusinessProduct,
)
from app.lib import log

__all__ = ["CpeBusinessProductController"]


if TYPE_CHECKING:
    from litestar.contrib.repository.filters import FilterTypes
    from litestar.dto import DTOData
    from litestar.pagination import OffsetPagination

    from app.domain.cpe_business_product.models import CPEBusinessProduct
    from app.domain.cpe_business_product.services import CPEBusinessProductService


logger = log.get_logger()


class CpeBusinessProductController(Controller):
    """CPE Business Product Controller."""

    tags = ["CPE Business Products"]
    guards = [requires_superuser]
    dependencies = {"cpes_business_service": Provide(provides_cpe_business_service)}
    return_dto = CpeBusinessDTO

    @get(
        operation_id="ListCPEBusinessProducts",
        name="cpebusinessproducts:list",
        summary="List CPE Business Products",
        cache_control=None,
        description="Retrieve the cpe business products",
        path=urls.CPE_BUSINESS_LIST,
    )
    async def list_cpe_business_product(
        self,
        cpes_business_service: CPEBusinessProductService,
        filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> OffsetPagination[CPEBusinessProduct]:
        """List business products."""
        results, total = await cpes_business_service.list_and_count(*filters)
        return cpes_business_service.to_dto(results, total, *filters)

    @get(
        operation_id="GetCPEBusinessProduct",
        name="cpebusinessproduct:get",
        path=urls.CPE_BUSINESS_DETAIL,
        summary="Retrieve the details of a CPE business product",
    )
    async def get_cpe_business_product(
        self,
        cpes_business_service: CPEBusinessProductService,
        product_id: str = Parameter(title="product id", description="The business product to retrieve"),
    ) -> CPEBusinessProduct:
        """Get a business product"""
        db_obj = await cpes_business_service.get(product_id)
        return cpes_business_service.to_dto(db_obj)

    @post(
        operation_id="CreateCPEBusinessProduct",
        name="cpebusinessproduct:create",
        summary="Create a new CPE business product",
        cache_control=None,
        description="A CPE business product",
        path=urls.CPE_BUSINESS_CREATE,
        dto=CreateCpeBusinessProductDTO,
    )
    async def create_cpe_business_product(
        self,
        cpes_business_service: CPEBusinessProductService,
        data: DTOData[CreateCPEBusinessProduct],
    ) -> CPEBusinessProduct:
        """Create a new business product."""
        obj = data.create_instance()
        db_obj = await cpes_business_service.create(obj.__dict__)
        return cpes_business_service.to_dto(db_obj)

    @patch(
        operation_id="UpdateCPEbusinessProduct",
        name="cpebusinessproduct:update",
        summary="Update CPE Business Product",
        path=urls.CPE_BUSINESS_UPDATE,
        dto=CPEBusinessProductUpdateDTO,
    )
    async def update_cpe_business_product(
        self,
        data: DTOData[UpdateCPEBusinessProduct],
        cpes_business_service: CPEBusinessProductService,
        product_id: str = Parameter(title="product id", description="The business product to update"),
    ) -> CPEBusinessProduct:
        """Update a business product"""
        obj = data.create_instance()
        db_obj = await cpes_business_service.update(product_id, obj.__dict__)
        return cpes_business_service.to_dto(db_obj)

    @delete(
        operation_id="DeleteCPEbusinessProduct",
        name="cpebusinessproduct:delete",
        path=urls.CPE_BUSINESS_DELETE,
        summary="Remove a CPE Business Product",
        cache_control=None,
        description="Removes a CPE Business Product",
        return_dto=None,
    )
    async def delete_cpe_business_product(
        self,
        cpes_business_service: CPEBusinessProductService,
        product_id: str = Parameter(
            title="CPE Business Product ID",
            description="The CPE business product id to delete.",
        ),
    ) -> None:
        """Delete a cpe from the system."""
        _ = await cpes_business_service.delete(product_id)
