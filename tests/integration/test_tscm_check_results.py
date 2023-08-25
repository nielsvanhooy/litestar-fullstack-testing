import datetime

from app.domain.tscm.dependencies import provides_tscm_check_results_service
from app.lib.db.base import session


######## refactor this back to the unit test part but for now its ok
async def test_tscm_check_results_date_compliancy() -> None:
    db = session()
    date = datetime.datetime.now().astimezone()
    async with db as db_session:
        tscm_check_result_service = await anext(provides_tscm_check_results_service(db_session=db_session))
        await tscm_check_result_service.compliant_since("TESM1234", date)
