"""Litestar-saqlalchemy exception types.

Also, defines functions that translate service and repository exceptions
into HTTP exceptions.
"""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotFoundException,
    PermissionDeniedException,
)
from litestar.middleware.exceptions._debug_response import create_debug_response
from litestar.middleware.exceptions.middleware import create_exception_response
from litestar.repository.exceptions import ConflictError, NotFoundError, RepositoryError
from litestar.status_codes import HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
from structlog.contextvars import bind_contextvars

if TYPE_CHECKING:
    from typing import Any

    from litestar.connection import Request
    from litestar.middleware.exceptions.middleware import ExceptionResponseContent
    from litestar.response import Response
    from litestar.types import Scope

__all__ = (
    "ConflictError",
    "AuthorizationError",
    "HealthCheckConfigurationError",
    "ApplicationError",
    "after_exception_hook_handler",
)


class ApplicationError(Exception):
    """Base exception type for the lib's custom exception types."""


class ApplicationClientError(ApplicationError):
    """Base exception type for client errors."""


class AuthorizationError(ApplicationClientError):
    """A user tried to do something they shouldn't have."""


class HealthCheckConfigurationError(ApplicationError):
    """An error occurred while registering an health check."""


class _HTTPConflictException(HTTPException):
    """Request conflict with the current state of the target resource."""

    status_code = HTTP_409_CONFLICT


async def after_exception_hook_handler(exc: Exception, _scope: Scope) -> None:
    """Binds `exc_info` key with exception instance as value to structlog
    context vars.

    This must be a coroutine so that it is not wrapped in a thread where we'll lose context.

    Args:
        exc: the exception that was raised.
        _scope: scope of the request
    """
    if isinstance(exc, ApplicationError):
        return
    if isinstance(exc, HTTPException) and exc.status_code < HTTP_500_INTERNAL_SERVER_ERROR:
        return
    bind_contextvars(exc_info=sys.exc_info())


def exception_to_http_response(
    request: Request[Any, Any, Any],
    exc: ApplicationError | RepositoryError,
) -> Response[ExceptionResponseContent]:
    """Transform repository exceptions to HTTP exceptions.

    Args:
        request: The request that experienced the exception.
        exc: Exception raised during handling of the request.

    Returns:
        Exception response appropriate to the type of original exception.
    """
    http_exc: type[HTTPException]
    if isinstance(exc, NotFoundError):
        http_exc = NotFoundException
    elif isinstance(exc, ConflictError | RepositoryError):
        http_exc = _HTTPConflictException
    elif isinstance(exc, AuthorizationError):
        http_exc = PermissionDeniedException
    else:
        http_exc = InternalServerException
    if request.app.debug:
        return create_debug_response(request, exc)
    return create_exception_response(request, http_exc(detail=str(exc.__cause__)))
