from gufo.ping import Ping
from multiprocessing import cpu_count

logger = log.get_logger()

# Maximal amounts of CPU used
MAX_CPU = 128 # refactor to settings and use core count
# Number of worker tasks within every thread
N_TASKS = 50 # refactor to settings

def ping_cpes(destinations: list[str]) -> None:
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

    results = []
    failed_results = []

    try:
        Ping().ping("0.0.0.0")
        result_queue = Queue()

        for retry_failed in range(3):
            workers = [
                Thread(
                    target=_root_worker,
                    args=(destinations[n::n_workers], result_queue, retry_failed + 1),
                    name=f"worker-{n}",
                )
                for n in range(n_workers)
            ]
            # Run threads

            for w in workers:
                w.start()

            for _ in range(n_data):
                addr, rtt = result_queue.get()
                if not rtt:
                    failed_results.append(addr)
                results.append((addr, rtt))

            destinations = failed_results

        return results

    except OSError:
        logger.debug("Looks like the software doesn't has root access. going for alternative method."
                     "if you want the full speed. make sure the software has root")
        result_queue = []




def _root_worker(data: List[str], result_queue: Queue, timeout: int = 1) -> None:
    """
    Thread worker, started within every thread.

    Args:
        data: List of IP addresses to ping.
        result_queue: Queue to push results back.
    """
    # Create separate event loop per each thread
    loop = asyncio.new_event_loop()
    # And set it as default
    asyncio.set_event_loop(loop)
    # Run asynchronous worker within every thread
    loop.run_until_complete(_root_async_worker(data, result_queue, timeout))
    # Cleanup
    loop.close()

async def _root_async_worker(data: List[str], result_queue: Queue, timeout) -> None:
    """
    Asynchronous worker. Started for each thread.

    Args:
        data: List of IP addresses to ping.
        result_queue: Queue to push results back.
    """
    # Create ping socket per each thread
    ping = Ping(size=128, timeout=timeout) # refactor size to settings
    addr_queue = asyncio.Queue(maxsize=2 * N_TASKS)

    finished = []
    # Effective tasks is limited by:
    # * Available addresses
    # * Imposed limit
    n_tasks = min(len(data), N_TASKS)

    # Create and run tasks
    loop = asyncio.get_running_loop()
    for _ in range(n_tasks):
        cond = asyncio.Event()
        loop.create_task(ping_task(ping, addr_queue, cond, result_queue))
        finished.append(cond)
    # Push data to address queue,
    # may be blocked if we'd pushed too many
    for x in data:
        await addr_queue.put(x)
    # Push stopping None for each task
    for _ in range(n_tasks):
        await addr_queue.put(None)
    # Wait for each task to complete
    for cond in finished:
        await cond.wait()

    return


async def ping_task(ping_socket, addr_queue: asyncio.Queue, done: asyncio.Event, result_queue: Queue) -> None:
    """
    Worker task. Up to N_TASKS spawn per thread.

    Args:
        addr_queue: Queue to pull addresses to ping. Stops when
            pulled None.
        done: Event to set when processing complete.
    """
    while True:
        # Pull address or None
        addr = await addr_queue.get()
        if not addr:
            # Stop on None
            break
        # Send ping and await the result
        print(addr)
        rtt = await ping_socket.ping(addr)
        # Push measured result to a main thread
        result_queue.put((addr, rtt))
    # Report worker is stopped.
    done.set()
