from logging import Logger
from typing import cast
from fastapi import HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError

from core.enums import LoggerCallerTypes
from core.schemas import ErrorDetailsSchema

from .responses import GenericErrorResponse


def request_validation_handler(request: Request, exc: Exception) -> Response:
    exc = cast(RequestValidationError, exc)
    error = exc.errors()[0]
    description = error["msg"]
    location = error["loc"][0]
    field = error["loc"][1] if len(error["loc"]) > 1 else None
    details = ErrorDetailsSchema(
        location=location, field=field, description=description
    )
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    logger: Logger = request.app.state.logger
    logger.error(
        description,
        extra=dict(
            caller=LoggerCallerTypes.validation_error.value,
            status_code=status_code,
            location=location,
            field=field,
        ),
    )
    return GenericErrorResponse(content=details, status_code=status_code)


def http_exception_handler(request: Request, exc: Exception) -> Response:
    exc = cast(HTTPException, exc)
    location = getattr(exc, "loc", None)
    field = getattr(exc, "field", None)
    description = exc.detail
    status_code = exc.status_code
    details = ErrorDetailsSchema(
        location=location, field=field, description=description
    )
    logger: Logger = request.app.state.logger
    logger.error(
        description,
        exc_info=exc,
        extra=dict(
            caller=LoggerCallerTypes.http_exception.value,
            status_code=status_code,
            location=location,
            field=field,
        )
    )
    return GenericErrorResponse(content=details, status_code=status_code)
