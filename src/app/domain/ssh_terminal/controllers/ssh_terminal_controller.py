"""CPE Business Service Controllers."""
from __future__ import annotations

from io import StringIO

import asyncssh
from litestar import Controller, WebSocket
from litestar.di import Provide
from litestar.handlers.websocket_handlers import websocket_listener

from app.domain import urls
from app.domain.cpe.dependencies import provides_cpe_service
from app.lib import log

__all__ = ["SshWebTerminalController"]
import asyncio

logger = log.get_logger()


class SshWebTerminalController(Controller):
    """SSH Web Terminal Controller."""

    tags = ["SSH Web Terminal Controller"]
    dependencies = {"cpe_service": Provide(provides_cpe_service)}

    @websocket_listener(
        path=urls.SSH_WEB_TERMINAL,
    )
    async def ssh_web_terminal(self, data: str, socket: WebSocket) -> str:
        # """ this is "a testing method, not for use now. but exploring options on what i want ""

        async with asyncssh.connect(
            "10.1.1.142",
            username="lagen008",
            password="lagen008",
            known_hosts=None,
            connect_timeout=10,
        ) as conn:
            output = StringIO()
            (sshWriter, sshReader, sshExReader) = await conn.open_session(
                term_type="vt100",
            )  # vt100 for cisco and huawi?
            ssh_task = asyncio.create_task(sshReader.read(1024))
            sshex_task = asyncio.create_task(sshExReader.read(1024))
            ws_task = asyncio.create_task(socket.receive_data(mode="text"))

            sshWriter.writelines(["term len 0\n"])
            while True:
                done, pending = await asyncio.wait([ws_task, ssh_task, sshex_task], return_when=asyncio.FIRST_COMPLETED)

                if ws_task in done:
                    msg = ws_task.result()
                    if "x03" in msg:
                        msg = "\x03"
                    else:
                        msg += "\r"
                    sshWriter.writelines([msg])
                    await sshWriter.drain()
                    ws_task = asyncio.create_task(socket.receive_data(mode="text"))

                if ssh_task in done:
                    data = ssh_task.result()
                    await socket.send_data(data)
                    ssh_task = asyncio.create_task(sshReader.read(1024))
                if sshex_task in done:
                    data = sshex_task.result()
                    await socket.send_data(data)
                    ssh_task = asyncio.create_task(sshExReader.read(1024))
