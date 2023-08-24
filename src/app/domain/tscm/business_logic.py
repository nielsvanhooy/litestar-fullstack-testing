from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.cpe.dependencies import provides_cpe_service
from app.domain.tscm.dependencies import provides_tscm_service
from app.lib.db.base import session
from app.domain.tscm.tscm import CpeTscmCheck
from app.lib import log
from app.lib import worker

from anyio import Path, run

if TYPE_CHECKING:
    from app.domain.tscm.models import TSCMCheck

logger = log.get_logger()




__all__ = ["perform_tscm_check"]


async def perform_tscm_check(device_id: str) -> list[TSCMCheck]:
    db = session()
    async with db as db_session:
        cpe_service = await anext(provides_cpe_service(db_session=db_session))
        tscm_service = await anext(provides_tscm_service(db_session=db_session))

        cpe = await cpe_service.get(device_id)
        vendor = cpe.vendor.name
        service = cpe.service.name

        tscm_checks =  await tscm_service.vendor_product_checks(
            vendor, service, cpe.product_configuration.cpe_model
        )
        email_results = []

        count = 0

        dir_path = Path('/workspace/app/configstore')
        async for path in dir_path.iterdir():

            logger.info("doing work on %s", path)
            if await path.is_file():
                provided_config = await path.read_text()

                tscm_check = CpeTscmCheck(
                    device_id=device_id, tscm_checks=tscm_checks, provided_config=provided_config, online_status=True, vendor=vendor, service=service
                )

                if not tscm_check.config_age_compliant(config_age=2):
                    results = tscm_check.results()
                    lawl = "lala"
                    # process results
                    email_results.append(results['tscm_email_doc'])

                if not tscm_check.online_status:
                    tscm_check.offline_compliant_not_compliant()
                    results = tscm_check.results()
                    # process results
                    lawl = "lala"
                else:
                    tscm_check.online_compliant_not_compliant()
                    results = tscm_check.results()
                    # process results
                    email_results.append(results['tscm_email_doc'])

            count += 1

        await worker.queues["background-tasks"].enqueue(
"send_email",
            subject="test",
            to=["test@test.nl","sjaakie@sjaakie.nl"],
            html="",
            timeout=60,
            template_body=email_results,
            template_name="tscm_email_template.html",
        )

        lala = "loloe"
