from enum import Enum
from typing import Annotated, Literal

from typing_extensions import Doc


class CaptchaService(Enum):
    cap_guru = "cap.guru"
    capmonster = "capmonster.cloud"


class Location(Enum):
    body = "body"
    path = "path"
    query = "query"
    header = "header"


class LicenseResultStatus(Enum):
    ok: Annotated[Literal["ok"], Doc("Success response")] = "ok"
    pending: Annotated[Literal["pending"], Doc("Request processing")] = (
        "pending"
    )
    not_authorized: Annotated[
        Literal["not_authorized"],
        Doc("Possible, session cookie has expired"),
    ] = "not_authorized"
    creds_not_found: Annotated[
        Literal["creds_not_found"],
        Doc("Username or script passed does not exist"),
    ] = "creds_not_found"
    error: Annotated[
        Literal["error"], Doc("All another unhandled errors")
    ] = "error"


class LoggerCallerTypes(Enum):
    common = "Common"
    validation_error = "Validation error"
    http_exception = "HTTP exception"
    http_error = "HTTP error"
