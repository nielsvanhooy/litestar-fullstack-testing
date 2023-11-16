import contextlib
import sys
from io import StringIO

__all__ = ["stdoutio"]

from collections.abc import Generator


@contextlib.contextmanager
def stdoutio() -> Generator[StringIO, None, None]:
    old = sys.stdout
    yield StringIO()
    sys.stdout = old
