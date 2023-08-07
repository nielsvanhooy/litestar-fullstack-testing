"""CPE Business Service Controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, delete, get, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter

from app.domain import urls
from app.domain.tscm.dependencies import provides_tscm_service
from app.domain.tscm.dtos import (
    TscmDTO,
CreateTscmCheck,
CreateTscmCheckDTO
)
from app.lib import log

__all__ = ["TscmController"]


if TYPE_CHECKING:
    from litestar.contrib.repository.filters import FilterTypes
    from litestar.dto import DTOData
    from litestar.pagination import OffsetPagination

    from app.domain.tscm.models import TSCMCheck
    from app.domain.tscm.services import TscmService


logger = log.get_logger()


class TscmController(Controller):
    """TSCM Controller."""

    tags = ["Tscm Security Checks"]
    dependencies = {"tscm_service": Provide(provides_tscm_service)}
    return_dto = TscmDTO

    @get(
        operation_id="ListTscmChecks",
        name="tscmchecks:list",
        summary="List TSCM Checks",
        cache_control=None,
        description="Retrieve TSCM Checks",
        path=urls.TSCM_LIST,
    )
    async def list_tscm_checks(
        self,
        tscm_service: TscmService,
        filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> OffsetPagination[TSCMCheck]:
        """List business products."""
        results, total = await tscm_service.list_and_count(*filters)
        return tscm_service.to_dto(results, total, *filters)

    @post(
        operation_id="CreateTscmCheck",
        name="tscmchecks:create",
        summary="Create a new TSCM Check",
        cache_control=None,
        description="Create a new TSCM Check",
        path=urls.TSCM_LIST_CREATE,
        dto=CreateTscmCheckDTO,
    )
    async def create_cpe_business_product(
        self,
        tscm_service: TscmService,
        data: DTOData[CreateTscmCheck],
    ) -> TSCMCheck:
        """Create a new business product."""
        obj = data.create_instance()
        db_obj = await tscm_service.create(obj.__dict__)
        return tscm_service.to_dto(db_obj)


    @delete(
        operation_id="DeleteTscmCheck",
        name="tscmchecks:delete",
        path=urls.TSCM_LIST_DELETE,
        summary="Remove a TSCM Check",
        cache_control=None,
        description="Removes a TSCM check",
        return_dto=None,
    )
    async def delete_tscm_check(
        self,
        tscm_service: TscmService,
        vendor_id: str = Parameter(
            title="The TSCM Check Id",
            description="The TSCM Check to delete",
        ),
    ) -> None:
        """Delete a tscm check from the system."""
        _ = await tscm_service.delete(vendor_id)
