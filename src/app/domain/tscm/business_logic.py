from app.domain.tscm.dependencies import provides_tscm_service

__all__ = ["perform_tscm_check"]


from app.lib.db.base import session


async def perform_tscm_check(device_id: str) -> None:
    db = session()
    async with db as db_session:
        tscm_service = await anext(provides_tscm_service(db_session=db_session))
        return await tscm_service.repository.vendor_product_checks("cisco", "VPN", "3600")
