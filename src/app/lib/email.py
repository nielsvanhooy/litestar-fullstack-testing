from __future__ import annotations

from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.lib import settings

mail_system = FastMail(ConnectionConfig(**settings.email.model_dump()))

__all__ = ["send_email"]


async def send_email(
    ctx: str,
    *,
    subject: str,
    to: list,
    html: str,
    attachments: list | None = None,
    template_body: Any,
    template_name: str,
) -> bool:
    """Args:
        ctx: an argument of SAQ worker
        subject: str = a subject for the email
        to: list of recipients
        html: the html string to send
        attachments: list of attachments defaults to empty list

    Returns:
        boolean True if mail was send
    """

    if attachments is None:
        attachments = []

    message = MessageSchema(
        subject=subject,
        recipients=to,
        body=html,
        subtype=MessageType.html,
        attachments=attachments,
        template_body=template_body,
    )
    if template_body and template_name:
        await mail_system.send_message(message, template_name=template_name)
    await mail_system.send_message(message)
    return True
