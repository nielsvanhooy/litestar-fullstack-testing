from multiprocessing import cpu_count

from gufo.ping import Ping

from app.lib import log, worker

__all__ = ["ping_cpes", "_ping"]

logger = log.get_logger()

# Maximal amounts of CPU used
MAX_CPU = 128  # refactor to settings and use core count
# Number of worker tasks within every thread
N_TASKS = 50  # refactor to settings


destinations = [
    "127.0.0.1",
    "127.0.0.2",
    "127.0.0.3",
    "192.176.4.2",
]


async def ping_cpes(_: dict) -> None:
    """Ping list of addresses.

    Args:
        path: Path to the list of IP addresses,
            each address on its own line
    """

    n_data = len(destinations)
    # Effective number of workers cannot be more than
    # * amount of addresses to ping
    # * available CPUs
    # * Imposed CPU limit
    n_workers = min(MAX_CPU, cpu_count(), n_data)

    await logger.ainfo("creating ping jobs")

    async def _ping_with_retries(destinations, succeeded, failed, retry: int = 0):
        """This is a recursive function"""
        await logger.ainfo("the global timeout is now  %s", retry)
        if retry == 3:
            await logger.ainfo("the timeout is now  %s", retry)
            return
        else:
            worker_ping_list = [destinations[n::n_workers] for n in range(n_workers)]
            await logger.ainfo("lets ping the new destinations %s", destinations)
            async with worker.queues["background-tasks"].batch():
                results = await worker.queues["background-tasks"].map(
                    _ping.__name__,
                    [{"destinations": ping_list, "ping_timeout": retry + 1} for ping_list in worker_ping_list],
                )

            failed = []

            await logger.ainfo(results)

            for worker_results in results:
                for ping_results in worker_results:
                    if ping_results:
                        if ping_results[1]:
                            succeeded.append((ping_results[0], ping_results[1]))
                        else:
                            failed.append(ping_results[0])

            new_destinations = failed
            await logger.ainfo(new_destinations)
            return await _ping_with_retries(new_destinations, succeeded, failed, retry + 1)


    succeeded = []
    failed = []

    await _ping_with_retries(destinations, succeeded, failed, retry=1)

    await logger.ainfo("done pinging")


async def _ping(ctx, *, destinations: list[str], ping_timeout: int = 1):
    results = []
    await logger.ainfo("the set timeout is now %s", ping_timeout)
    ping = Ping(size=64, timeout=ping_timeout)
    for destination in destinations:
        rtt = await ping.ping(destination)
        if rtt:
            results.append((destination, True))
        else:
            results.append((destination, False))

    return results


# def _root_worker(data: List[str], result_queue: Queue, timeout: int = 1) -> None:
#     """
#     Thread worker, started within every thread.
#
#     Args:
#         data: List of IP addresses to ping.
#         result_queue: Queue to push results back.
#     """
#     # Create separate event loop per each thread
#     # And set it as default
#     # Run asynchronous worker within every thread
#     # Cleanup
#
# async def _root_async_worker(data: List[str], result_queue: Queue, timeout) -> None:
#     """
#     Asynchronous worker. Started for each thread.
#
#     Args:
#         data: List of IP addresses to ping.
#         result_queue: Queue to push results back.
#     """
#     # Create ping socket per each thread
#
#     # Effective tasks is limited by:
#     # * Available addresses
#     # * Imposed limit
#
#     # Create and run tasks
#     for _ in range(n_tasks):
#     # Push data to address queue,
#     # may be blocked if we'd pushed too many
#     for x in data:
#     # Push stopping None for each task
#     for _ in range(n_tasks):
#     # Wait for each task to complete
#     for cond in finished:
#
#
#
# async def ping_task(ping_socket, addr_queue: asyncio.Queue, done: asyncio.Event, result_queue: Queue) -> None:
#     """
#     Worker task. Up to N_TASKS spawn per thread.
#
#     Args:
#         addr_queue: Queue to pull addresses to ping. Stops when
#             pulled None.
#         done: Event to set when processing complete.
#     """
#     while True:
#         # Pull address or None
#         if not addr:
#             # Stop on None
#         # Send ping and await the result
#         # Push measured result to a main thread
#     # Report worker is stopped.
