from collections.abc import Callable
from typing import Any

from gufo.ping import Ping

__all__ = ["ping", "retry_with_backoff"]


def retry_with_backoff(retries: int = 3, initial_timeout: int = 1) -> Any:
    def rwb(f: Callable) -> Callable:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            x = 0
            while True:
                try:
                    return await f(*args, **kwargs)
                except TimeoutError:
                    if x == retries:
                        return False
                # count like 1, 2 ,3 ,4 ,5 (until max retries)
                # retries 3 makes 4 total.
                kwargs["timeout"] = initial_timeout + 1 + x
                x += 1

        return wrapper

    return rwb


@retry_with_backoff(retries=2)  # type: ignore[misc]
async def ping(timeout: int = 1) -> bool:
    ping = Ping(timeout=timeout)
    r = await ping.ping("10.1.1.142")
    if not r:
        raise TimeoutError("Destination Unreachable")
    return True
