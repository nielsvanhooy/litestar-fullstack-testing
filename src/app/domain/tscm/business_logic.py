from __future__ import annotations

import time
from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from anyio import Path, create_task_group

from app.domain.cpe.dependencies import provides_cpe_service
from app.domain.tscm.dependencies import provides_tscm_check_results_service, provides_tscm_service
from app.domain.tscm.tscm import CpeTscmCheck, TSCMEmailDoc, TscmExportReport
from app.lib import log, worker
from app.lib.data_exporter import ElasticSearchRepository
from app.lib.db.base import session

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from app.domain.tscm.models import TSCMCheck

logger = log.get_logger()


__all__ = ["perform_tscm_check"]


async def elastic_bulk_iterator(index: str, results: list) -> AsyncGenerator:
    for result in results:
        yield {"_index": index, "doc": asdict(result)}


async def export_to_elastic(results: dict[Any, Any], elasticsearch_repo: ElasticSearchRepository) -> None:
    for key, value in results.items():
        if isinstance(value, list):
            index = key
            await elasticsearch_repo.bulk(iterator=elastic_bulk_iterator(index, value))


async def perform_tscm_check(
    device_id: str,
    selected_check: str | None = None,
    test_run: bool = False,
) -> list[TSCMCheck]:  # type: ignore
    db = session()
    async with db as db_session:
        cpe_service = await anext(provides_cpe_service(db_session=db_session))
        tscm_service = await anext(provides_tscm_service(db_session=db_session))
        tscm_check_result_service = await anext(provides_tscm_check_results_service(db_session=db_session))

        export_report = TscmExportReport()
        elasticsearch_repo = ElasticSearchRepository(test_run=test_run)

        cpe = await cpe_service.get(device_id)

        tscm_checks = await tscm_service.vendor_product_checks(
            cpe.vendor.name,
            cpe.service.name,
            cpe.product_configuration.cpe_model,
            selected_check,
        )
        latest_compliancy = await tscm_check_result_service.compliant_since(device_id)

        email_results: list[TSCMEmailDoc] = []

        time.time()
        async with create_task_group() as task_group:
            dir_path = Path("/home/donnyio/git/configstore/kpnvpn")
            async for path in dir_path.iterdir():
                logger.info("doing work on %s", path)
                if await path.is_file():
                    provided_config = await path.read_text()

                    task_group.start_soon(
                        process_file,
                        tscm_checks,
                        provided_config,
                        device_id,
                        cpe.online_status,
                        cpe.vendor.name,
                        cpe.service.name,
                        export_report,
                        email_results,
                        latest_compliancy,
                    )

        tscm_export_results = export_report.results()
        await export_to_elastic(tscm_export_results, elasticsearch_repo)

        await worker.queues["background-tasks"].enqueue(
            "send_email",
            subject="test",
            to=["test@test.nl", "sjaakie@sjaakie.nl"],
            html="",
            timeout=60,
            template_body=email_results,
            template_name="tscm_email_template.html",
        )


async def process_file(
    tscm_checks: list[TSCMCheck],
    provided_config: str,
    device_id: str,
    online_status: bool,
    vendor: str,
    service: str,
    report: TscmExportReport,
    email_results: list[TSCMEmailDoc],
    latest_compliancy: bool,
) -> None:
    tscm_check = CpeTscmCheck(
        device_id=device_id,
        tscm_checks=tscm_checks,
        provided_config=provided_config,
        online_status=online_status,
        vendor=vendor,
        service=service,
        report=report,
    )

    if not tscm_check.config_age_compliant(config_age=2):
        # process results
        email_results.append(tscm_check.get_email_results())

    if not tscm_check.online_status:
        tscm_check.offline_compliant_not_compliant(latest_compliancy)
    else:
        tscm_check.online_compliant_not_compliant()

    # process results
    email_results.append(tscm_check.get_email_results())
