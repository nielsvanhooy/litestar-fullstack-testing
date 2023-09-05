from multiprocessing import cpu_count
from typing import Any

from gufo.ping import Ping

from app.domain.cpe.dependencies import provides_cpe_service
from app.lib import log, worker
from app.lib.db.base import session

__all__ = ["ping_cpes", "_ping"]

logger = log.get_logger()

# Maximal amounts of CPU used
MAX_CPU = 128  # refactor to settings and use core count
# Number of worker tasks within every thread
N_TASKS = 50  # refactor to settings
RETRY_LIMIT = 3  # refactor to settings


destinationss: dict[str, Any] = {
    "10.1.1.142": {"device_id": "TESM1233", "mgmt_ip": "10.1.1.142"},
    "10.1.1.156": {"device_id": "TESM1234", "mgmt_ip": "10.1.1.156"},
}


async def ping_cpes(_: dict) -> None:
    """Ping list of addresses."""

    async def _ping_with_retries(
        destinations: list[str], succeeded: dict[str, Any], failed: list[str], retry: int = 0
    ) -> dict[str, Any]:
        """This is a recursive function"""
        if retry == RETRY_LIMIT:
            converted_failed = {
                dest: {
                    "mgmt_ip": dest,
                    "online_status": False,
                }
                for dest in failed
            }

            return succeeded | converted_failed

        worker_ping_list = [destinations[n::n_workers] for n in range(n_workers)]
        async with worker.queues["background-tasks"].batch():
            results = await worker.queues["background-tasks"].map(
                _ping.__name__,
                [{"destinations": ping_list, "ping_timeout": retry + 1} for ping_list in worker_ping_list],
            )

        failed = []

        for worker_results in results:
            for ping_results in worker_results:
                if ping_results:
                    if ping_results[1]:
                        succeeded[ping_results[0]] = {"mgmt_ip": ping_results[0], "online_status": ping_results[1]}
                    else:
                        failed.append(ping_results[0])

        new_destinations = failed
        return await _ping_with_retries(new_destinations, succeeded, failed, retry + 1)

    db = session()
    async with db as db_session:
        cpe_service = await anext(provides_cpe_service(db_session=db_session))
        await cpe_service.get_cpes_to_ping()

        destinations: list[str] = list(destinationss.keys())
        n_data = len(destinations)
        # Effective number of workers cannot be more than
        # * amount of addresses to ping
        # * available CPUs
        # * Imposed CPU limit
        n_workers = min(MAX_CPU, cpu_count(), n_data)

        await logger.ainfo("creating ping jobs")

        results = await _ping_with_retries(destinations, succeeded={}, failed=[], retry=1)

        for key, result in results.items():
            if key in destinationss:
                destinationss[key].update(result)

        await logger.ainfo("done pinging %s destinations. committing results to db", len(destinations))
        await cpe_service.update_many(list(destinationss.values()))
        await logger.ainfo("Done")


async def _ping(ctx: str, *, destinations: list[str], ping_timeout: int = 1) -> list[tuple[str, bool]]:
    results = []
    ping = Ping(size=64, timeout=ping_timeout)
    for destination in destinations:
        rtt = await ping.ping(destination)
        if rtt:
            results.append((destination, True))
        else:
            results.append((destination, False))

    return results
