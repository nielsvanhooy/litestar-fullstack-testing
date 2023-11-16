import pytest
from pathlib import Path

from app.lib.email import mail_system, send_email

pytestmark = pytest.mark.anyio


async def test_send_email() -> None:
    subject = "test-mail"
    to = ["lala@lala.nl", "loeloe@loeloe.nl"]
    html = """<p>Hi this test mail, thanks for using litestar-mail</p> """

    # Enable Suppress send to mock the sending.
    mail_system.config.SUPPRESS_SEND = 1
    with mail_system.record_messages() as outbox:
        # the ctx is a fake argument. normally needed for SAQ background worker
        await send_email("ctx", subject=subject, to=to, html=html)

    assert outbox[0]["subject"] == subject
    assert outbox[0]["to"] == "lala@lala.nl, loeloe@loeloe.nl"


async def test_send_email_with_file() -> None:
    subject = "test-mail"
    to = ["lala@lala.nl", "loeloe@loeloe.nl"]
    html = """<p>Hi this test mail, thanks for using litestar-mail</p> """

    directory = Path.cwd()
    attachment = [f"{directory}/tests/lib_utils/lib/txt_files/plain.txt"]
    if directory.name == "lib":
        attachment = [f"{directory}/txt_files/plain.txt"]

    # Enable Suppress send to mock the sending.
    mail_system.config.SUPPRESS_SEND = 1
    with mail_system.record_messages() as outbox:
        # the ctx is a fake argument. normally needed for SAQ background worker
        await send_email("ctx", subject=subject, to=to, html=html, attachments=attachment)

    assert outbox[0]._payload[1].__dict__.get("_headers")[3][1] == "attachment; filename*=UTF8''plain.txt"
