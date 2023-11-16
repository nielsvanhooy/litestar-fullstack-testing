"""CPE Controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter

from app.domain import urls
from app.domain.cpe.business_logic import readout_cpe
from app.domain.cpe.dependencies import provides_cpe_service
from app.domain.cpe.dtos import CpeDTO, CPEUpdateDTO, CreateCPE, CreateCpeDTO, ReadoutCpeDTO, UpdateCPE
from app.lib import log

__all__ = ["CpeController"]

if TYPE_CHECKING:
    from litestar.dto import DTOData
    from litestar.pagination import OffsetPagination

    from app.domain.cpe.models import CPE
    from app.domain.cpe.services import CPEService
    from app.lib.dependencies import FilterTypes

logger = log.get_logger()


class CpeController(Controller):
    """Account Controller."""

    tags = ["CPES"]
    dependencies = {"cpes_service": Provide(provides_cpe_service)}
    return_dto = CpeDTO

    @get(
        operation_id="ListCPEs",
        name="cpes:list",
        summary="List CPEs",
        cache_control=None,
        description="Retrieve the cpe's",
        path=urls.CPES_LIST,
    )
    async def list_cpes(
        self,
        cpes_service: CPEService,
        filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> OffsetPagination[CPE]:
        """List users."""
        results, total = await cpes_service.list_and_count(*filters)
        return cpes_service.to_dto(results, total, *filters)

    @get(
        operation_id="GetCPE",
        name="cpes:get",
        path=urls.CPES_DETAIL,
        summary="Retrieve the details of a cpe",
    )
    async def get_cpe(
        self,
        cpes_service: CPEService,
        device_id: str = Parameter(title="device id", description="The device to retrieve"),
    ) -> CPE:
        """Get a CPE"""
        db_obj = await cpes_service.get(device_id)
        return cpes_service.to_dto(db_obj)

    @post(
        operation_id="CreateCPE",
        name="cpes:create",
        summary="Create a new CPE (customer premises equipment)",
        cache_control=None,
        description="A CPE",
        path=urls.CPES_CREATE,
        dto=CreateCpeDTO,
    )
    async def create_cpe(
        self,
        cpes_service: CPEService,
        data: DTOData[CreateCPE],
    ) -> CPE:
        """Create a new cpe."""
        obj = data.create_instance()
        db_obj = await cpes_service.create(obj.__dict__)
        return cpes_service.to_dto(db_obj)

    @patch(
        operation_id="UpdateCPE",
        name="CPES:update",
        summary="Update CPE",
        path=urls.CPES_UPDATE,
        dto=CPEUpdateDTO,
    )
    async def update_cpe(
        self,
        data: DTOData[UpdateCPE],
        cpes_service: CPEService,
        device_id: str = Parameter(title="device id", description="The device to update"),
    ) -> CPE:
        """Update a CPE"""
        obj = data.create_instance()
        db_obj = await cpes_service.update(item_id=device_id, data=obj.__dict__)
        return cpes_service.to_dto(db_obj)

    @delete(
        operation_id="DeleteCPE",
        name="CPES:delete",
        path=urls.CPES_DELETE,
        summary="Remove CPE",
        cache_control=None,
        description="Removes a CPE and all associated data from the system.",
        return_dto=None,
    )
    async def delete_cpe(
        self,
        cpes_service: CPEService,
        device_id: str = Parameter(
            title="CPE ID",
            description="The CPE to delete.",
        ),
    ) -> None:
        """Delete a cpe from the system."""
        _ = await cpes_service.delete(device_id)

    @post(
        operation_id="ReadoutCPE",
        name="cpes:readout",
        summary="Perform a readout of a CPE",
        cache_control=None,
        description="readout cpe",
        path=urls.CPES_READOUT,
        dto=ReadoutCpeDTO,
    )
    async def readout_cpe(
        self,
        cpes_service: CPEService,
        device_id: str = Parameter(
            title="CPE ID",
            description="The CPE to perform a readout on.",
        ),
    ) -> CPE:
        db_obj = await cpes_service.get(device_id)
        await readout_cpe(db_obj.mgmt_ip, db_obj.os)
        """Readout a CPE"""
        return cpes_service.to_dto(db_obj)
