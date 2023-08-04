"""CPE Business Service Controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter

from app.domain import urls
from app.domain.accounts.guards import requires_superuser
from app.domain.cpe_vendor.dependencies import provides_cpe_vendor_service
from app.domain.cpe_vendor.dtos import CpeVendorDTO, CreateUpdateCPEVendor, CreateUpdateCPEVendorDTO
from app.lib import log

__all__ = ["CpeVendorController"]


if TYPE_CHECKING:
    from litestar.contrib.repository.filters import FilterTypes
    from litestar.dto import DTOData
    from litestar.pagination import OffsetPagination

    from app.domain.cpe_vendor.models import CPEVendor
    from app.domain.cpe_vendor.services import CPEVendorService


logger = log.get_logger()


class CpeVendorController(Controller):
    """Account Controller."""

    tags = ["CPE Vendors"]
    guards = [requires_superuser]
    dependencies = {"cpes_vendor_service": Provide(provides_cpe_vendor_service)}
    return_dto = CpeVendorDTO

    @get(
        operation_id="ListCPEVendors",
        name="cpevendors:list",
        summary="List CPE Vendors",
        cache_control=None,
        description="Retrieve the cpe vendors",
        path=urls.CPE_VENDORS_LIST,
    )
    async def list_cpe_vendors(
        self, cpes_vendor_service: CPEVendorService, filters: list[FilterTypes] = Dependency(skip_validation=True)
    ) -> OffsetPagination[CPEVendor]:
        """List users."""
        results, total = await cpes_vendor_service.list_and_count(*filters)
        return cpes_vendor_service.to_dto(results, total, *filters)

    @get(
        operation_id="GetCPEVendor",
        name="cpevendors:get",
        path=urls.CPE_VENDORS_DETAIL,
        summary="Retrieve the details of a cpe vendor",
    )
    async def get_cpe_vendor(
        self,
        cpes_vendor_service: CPEVendorService,
        product_id: str = Parameter(title="product id", description="The business product to retrieve"),
    ) -> CPEVendor:
        """Get a business product"""
        db_obj = await cpes_vendor_service.get(product_id)
        return cpes_vendor_service.to_dto(db_obj)

    @post(
        operation_id="CreateCPEVendors",
        name="cpevendors:create",
        summary="Create a new CPE Vendor",
        cache_control=None,
        description="A CPE Vendor",
        path=urls.CPE_VENDORS_CREATE,
        dto=CreateUpdateCPEVendorDTO,
    )
    async def create_cpe_vendor(
        self,
        cpes_vendor_service: CPEVendorService,
        data: DTOData[CreateUpdateCPEVendor],
    ) -> CPEVendor:
        """Create a new business product."""
        obj = data.create_instance()
        db_obj = await cpes_vendor_service.create(obj.__dict__)
        return cpes_vendor_service.to_dto(db_obj)

    @patch(
        operation_id="UpdateCPEVendor",
        name="cpevendors:update",
        summary="Update CPE Vendor",
        path=urls.CPE_VENDORS_UPDATE,
        dto=CreateUpdateCPEVendorDTO,
    )
    async def update_cpe_vendor(
        self,
        data: DTOData[CreateUpdateCPEVendor],
        cpes_vendor_service: CPEVendorService,
        product_id: str = Parameter(title="product id", description="The business product to update"),
    ) -> CPEVendor:
        """Update a business product"""
        obj = data.create_instance()
        db_obj = await cpes_vendor_service.update(product_id, obj.__dict__)
        return cpes_vendor_service.to_dto(db_obj)

    @delete(
        operation_id="DeleteCPEVendor",
        name="cpevendors:delete",
        path=urls.CPE_VENDORS_DELETE,
        summary="Remove a CPE Vendor",
        cache_control=None,
        description="Removes a CPE Vendor",
        return_dto=None,
    )
    async def delete_cpe_vendor(
        self,
        cpes_vendor_service: CPEVendorService,
        product_id: str = Parameter(
            title="CPE Business Product ID",
            description="The CPE business product id to delete.",
        ),
    ) -> None:
        """Delete a cpe from the system."""
        _ = await cpes_vendor_service.delete(product_id)
