import datetime
from typing import Any

from advanced_alchemy.filters import BeforeAfter, LimitOffset
from sqlalchemy import and_, select

from app.domain.cpe.dependencies import provides_cpe_service
from app.domain.cpe.models import CPE
from app.domain.cpe_business_product.dependencies import provides_cpe_business_service
from app.domain.cpe_business_product.models import CPEBusinessProduct
from app.domain.cpe_vendor.dependencies import provides_cpe_vendor_service
from app.domain.cpe_vendor.models import CPEVendor
from app.domain.tscm.models import TSCMCheck, TSCMCheckResult
from app.lib import settings
from app.lib.dependencies import FilterTypes
from app.lib.repository import SQLAlchemyAsyncRepository
from app.lib.service import SQLAlchemyAsyncRepositoryService

__all__ = ["TscmService", "TscmRepository", "TscmCheckResultService", "TscmCheckResultRepository"]


class TscmRepository(SQLAlchemyAsyncRepository[TSCMCheck]):
    """TSCM Sqlalchemy Repository"""

    model_type = TSCMCheck

    async def vendor_product_checks(
        self,
        vendor_name: str,
        business_product_name: str,
        model_name: str,
        selected_check: str | None,
    ) -> list[TSCMCheck]:
        """Statement for TSCM Checks based on the vendor and business product for a device
        todo The statement is perhaps still basic as of aug 8 still learning sqlalchemy 2.0
        """
        if selected_check:
            return await self.list(
                statement=(
                    select(TSCMCheck)
                    .join(TSCMCheck.vendor)
                    .join(TSCMCheck.service)
                    .where(
                        and_(
                            CPEVendor.name == vendor_name,
                            CPEBusinessProduct.name == business_product_name,
                            TSCMCheck.key == selected_check,
                        ),
                    )
                ),
            )

        base_query = (
            select(TSCMCheck)
            .join(TSCMCheck.vendor)
            .join(TSCMCheck.service)
            .where(
                and_(
                    CPEVendor.name == vendor_name,
                    CPEBusinessProduct.name == business_product_name,
                    TSCMCheck.active == True,
                ),
            )
        )

        child_tasks = await self.list(statement=base_query.filter(TSCMCheck.device_model == model_name))

        if child_tasks and model_name != "All":
            # if there are child_tasks we filter out the parents of the child.
            parent_names = [task.replaces_parent_check for task in child_tasks]
            return await self.list(statement=base_query.filter(~TSCMCheck.key.in_(parent_names)))

        # if no child checks then we get only the ones marked as parent "ALL"
        return await self.list(statement=base_query.filter(TSCMCheck.replaces_parent_check == "None"))


class TscmService(SQLAlchemyAsyncRepositoryService[TSCMCheck]):
    repository_type = TscmRepository

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: TscmRepository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

    async def create(self, data: TSCMCheck | dict[str, Any]) -> TSCMCheck:
        """Create a new TSCM check with relation service and vendor"""

        if isinstance(data, dict):
            data_business_product_id = data.get("business_service", None)
            data_vendor_id = data.get("vendor", None)

        business_service = await anext(provides_cpe_business_service(db_session=self.repository.session))
        business_product = await business_service.get(data_business_product_id, id_attribute="name")

        vendor_service = await anext(provides_cpe_vendor_service(db_session=self.repository.session))
        vendor_product = await vendor_service.get(data_vendor_id, id_attribute="name")

        db_obj = await self.to_model(data, "create")
        db_obj.vendor = vendor_product
        db_obj.service = business_product

        return await super().create(db_obj)

    async def vendor_product_checks(
        self,
        vendor_name: str,
        business_product_name: str,
        model_name: str = "All",
        selected_check: str | None = None,
    ) -> list[TSCMCheck]:
        """Gets the TSCM Checks based on the vendor and business product for a device"""
        return await self.repository.vendor_product_checks(
            vendor_name,
            business_product_name,
            model_name,
            selected_check,
        )


class TscmCheckResultRepository(SQLAlchemyAsyncRepository[TSCMCheckResult]):
    """Tscm check results Sqlalchemy Repository"""

    model_type = TSCMCheckResult

    async def exists(self, *filters: FilterTypes, **kwargs: Any) -> bool:  # type: ignore
        """Return true if the object specified by ``kwargs`` exists.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Identifier of the instance to be retrieved.

        Returns:
            True if the instance was found.  False if not found..

        """
        existing = await self.count(*filters, **kwargs)
        return existing > 0

    async def compliant_since(self, device_id: str) -> bool:
        """device_id: device_id of the CPE to check
        return: boolean

        function does three things.
        1: check if there are any results. if not return False
        2: check the latest record if the device was online and returns the corresponding value
        3: if check 2 was False then it looks back to older records to verify if the CPE was compliant
        in the timerange from MAXIMUM_CONFIG_AGE until now
        """
        current_date = datetime.datetime.now().astimezone()
        limit_filter = LimitOffset(limit=1, offset=0)
        date_filter = BeforeAfter(
            field_name="date",
            after=current_date - datetime.timedelta(days=settings.tscm.MAXIMUM_CONFIG_AGE),
            before=current_date,
        )

        base_query = select(TSCMCheckResult).join(CPE).where(and_(CPE.device_id == device_id))
        tscm_check_results = await self.count(statement=base_query)
        if not tscm_check_results:
            return False

        # find the latest record and check if the device was online
        latest = await self.list(limit_filter, statement=base_query.order_by(TSCMCheckResult.date.desc()))

        if not latest[0].is_online:
            return await self.exists(
                limit_filter,
                date_filter,
                statement=base_query.filter(TSCMCheckResult.is_compliant == True, TSCMCheckResult.is_online == True),
            )
        return latest[0].is_compliant


class TscmCheckResultService(SQLAlchemyAsyncRepositoryService[TSCMCheckResult]):
    repository_type = TscmCheckResultRepository

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: TscmCheckResultRepository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

    async def create(self, data: TSCMCheckResult | dict[str, Any]) -> TSCMCheckResult:
        """Create a new TSCM check result with relation to CPE"""

        if isinstance(data, dict):
            data_device_id = data.get("device_id", None)

        cpe_service = await anext(provides_cpe_service(db_session=self.repository.session))
        cpe = await cpe_service.get(data_device_id, id_attribute="device_id")

        db_obj = await self.to_model(data, "create")
        db_obj.cpe_id = cpe.device_id

        return await super().create(db_obj)

    async def compliant_since(self, device_id: str) -> bool:
        return await self.repository.compliant_since(device_id)
