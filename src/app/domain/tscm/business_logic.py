from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from anyio import Path

from app.domain.cpe.dependencies import provides_cpe_service
from app.domain.tscm.dependencies import provides_tscm_check_results_service, provides_tscm_service
from app.domain.tscm.tscm import CpeTscmCheck, TSCMDoc, TSCMPerCheckDetailDoc
from app.lib import log
from app.lib.data_exporter import ElasticSearchRepository
from app.lib.db.base import session

if TYPE_CHECKING:
    from app.domain.tscm.models import TSCMCheck

logger = log.get_logger()


__all__ = ["perform_tscm_check"]


async def export_to_elastic(results: dict[Any, Any], elasticsearch_repo: ElasticSearchRepository) -> None:
    for value in results.values():
        if isinstance(value, list):
            for tscm_check_doc in value:
                if isinstance(tscm_check_doc, TSCMPerCheckDetailDoc):
                    await elasticsearch_repo.add(tscm_check_doc)

        if isinstance(value, TSCMDoc):
            await elasticsearch_repo.add(value)


async def perform_tscm_check(device_id: str) -> list[TSCMCheck]:
    db = session()
    async with db as db_session:
        cpe_service = await anext(provides_cpe_service(db_session=db_session))
        tscm_service = await anext(provides_tscm_service(db_session=db_session))
        tscm_check_result_service = await anext(provides_tscm_check_results_service(db_session=db_session))
        ElasticSearchRepository()

        cpe = await cpe_service.get(device_id)
        vendor = cpe.vendor.name
        service = cpe.service.name
        device_model = cpe.product_configuration.cpe_model

        tscm_checks = await tscm_service.vendor_product_checks(vendor, service, device_model)
        latest_compliancy = await tscm_check_result_service.compliant_since(device_id)
        email_results = []

        count = 0

        start = time.time()
        dir_path = Path("/home/donnyio/git/configstore/kpnvpn")
        async for path in dir_path.iterdir():
            logger.info("doing work on %s", path)
            if await path.is_file():
                provided_config = await path.read_text()

                tscm_check = CpeTscmCheck(
                    device_id=device_id,
                    tscm_checks=tscm_checks,
                    provided_config=provided_config,
                    online_status=True,
                    vendor=vendor,
                    service=service,
                )

                if not tscm_check.config_age_compliant(config_age=2):
                    results = tscm_check.results()
                    # process results
                    email_results.append(results["tscm_email_doc"])

                if not tscm_check.online_status:
                    tscm_check.offline_compliant_not_compliant(latest_compliancy)
                    # process results
                    results = tscm_check.results()
                else:
                    tscm_check.online_compliant_not_compliant()
                    results = tscm_check.results()
                    # process results
                    email_results.append(results["tscm_email_doc"])
        count += 1
        end = time.time()
        end - start

        # await worker.queues["background-tasks"].enqueue(
        #     "send_email",
