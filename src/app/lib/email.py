from __future__ import annotations

from fastapi_mail import MessageSchema, MessageType, FastMail, ConnectionConfig

from app.lib import settings

mail_system = FastMail(ConnectionConfig(**settings.email.model_dump()))

__all__ = [
    "send_email"
]

async def send_email(ctx, *, subject: str, to: list, html: str, attachments: list | None = None) -> bool:
    """Args:
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
        subject=subject, recipients=to, body=html, subtype=MessageType.html, attachments=attachments
    )

    await mail_system.send_message(message)
    return True
