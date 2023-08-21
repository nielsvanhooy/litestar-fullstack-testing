from typing import Any

from sqlalchemy import and_, select

from app.domain.cpe_business_product.models import CPEBusinessProduct
from app.domain.cpe_vendor.models import CPEVendor
from app.domain.tscm.models import TSCMCheck
from app.lib.repository import SQLAlchemyAsyncRepository
from app.lib.service.sqlalchemy import SQLAlchemyAsyncRepositoryService

__all__ = ["TscmService", "TscmRepository"]

from app.domain.cpe_business_product.dependencies import provides_cpe_business_service
from app.domain.cpe_vendor.dependencies import provides_cpe_vendor_service


class TscmRepository(SQLAlchemyAsyncRepository[TSCMCheck]):
    """CPE Sqlalchemy Repository"""

    model_type = TSCMCheck

    async def vendor_product_checks(
        self, vendor_name: str, business_product_name: str, model_name: str = "All"
    ) -> list[TSCMCheck]:
        """Statement for TSCM Checks based on the vendor and business product for a device
        todo The statement is perhaps still basic as of aug 8 still learning sqlalchemy 2.0
        """
        if selected_check := None:
            await self.list(
                statement=(
                    select(TSCMCheck)
                    .join(TSCMCheck.vendor)
                    .join(TSCMCheck.service)
                    .where(
                        and_(
                            CPEVendor.name == vendor_name,
                            CPEBusinessProduct.name == business_product_name,
                            TSCMCheck.key == selected_check,
                        )
                    )
                )
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
                )
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

    async def vendor_product_checks(self, vendor_name: str, business_product_name: str) -> list[TSCMCheck]:
        """Gets the TSCM Checks based on the vendor and business product for a device"""
        return await self.repository.vendor_product_checks(vendor_name, business_product_name)
