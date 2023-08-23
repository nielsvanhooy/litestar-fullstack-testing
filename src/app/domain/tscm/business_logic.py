from app.domain.cpe.dependencies import provides_cpe_service
from app.domain.tscm.dependencies import provides_tscm_service

__all__ = ["perform_tscm_check"]


from app.lib.db.base import session


async def perform_tscm_check(device_id: str) -> None:
    db = session()
    async with db as db_session:
        cpe_service = await anext(provides_cpe_service(db_session=db_session))
        tscm_service = await anext(provides_tscm_service(db_session=db_session))

        cpe = await cpe_service.get(device_id)
        return await tscm_service.vendor_product_checks(
            cpe.vendor.name, cpe.service.name, cpe.product_configuration.cpe_model
        )
