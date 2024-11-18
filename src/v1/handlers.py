from typing import cast
from fastapi import HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError

from core.schemas import ErrorDetailsSchema

from .responses import GenericErrorResponse


def request_validation_handler(
    _: Request, exc: Exception
) -> Response:
    exc = cast(RequestValidationError, exc)
    error = exc.errors()[0]
    description = error["msg"]
    field = error["loc"][1] if len(error["loc"]) > 1 else None
    details = ErrorDetailsSchema(
        location=error["loc"][0], field=field, description=description
    )
    return GenericErrorResponse(
        content=details, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
)


def http_exception_handler(
    _: Request, exc: Exception
) -> Response:
    exc = cast(HTTPException, exc)
    details = ErrorDetailsSchema(
        location=getattr(exc, "loc", None),
        field=getattr(exc, "field", None),
        description=exc.detail,
    )
    return GenericErrorResponse(content=details, status_code=exc.status_code)
