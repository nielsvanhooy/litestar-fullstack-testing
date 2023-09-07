from app.domain.cpe.dependencies import provides_cpe_service
from app.lib.db.base import session


######## refactor this back to the unit test part but for now its ok
async def test_get_cpes_to_ping() -> None:
    db = session()
    async with db as db_session:
        cpe_service = await anext(provides_cpe_service(db_session=db_session))
        cpes_to_ping = await cpe_service.get_cpes_to_ping()
        assert len(cpes_to_ping) > 0
        assert "mgmt_ip" in cpes_to_ping["10.1.1.142"]
