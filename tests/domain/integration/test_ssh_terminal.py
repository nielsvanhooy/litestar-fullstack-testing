from typing import TYPE_CHECKING
import aiohttp
import httpx
import pytest
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from httpx import AsyncClient
if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_ssh_terminal(app, superuser_token_headers: dict[str, str]) -> None:
    async with AsyncClient(transport=ASGIWebSocketTransport(app), base_url='http://0.0.0.0:8000', headers=superuser_token_headers) as client:
        async with aconnect_ws("/api/terminal", client) as ws:
            await ws.send_text("df -h")
            # anyio.from_thread.start_blocking_portal("asyncio")  bug in lib pull request is done but not new release yet
            data = await ws.send_text("df -h")
            message = await ws.receive_text()
            print(message)
            await ws.send_text("Hello!")
