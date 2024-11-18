from http.cookies import SimpleCookie
from typing import Any

from multidict import CIMultiDictProxy
from pydantic import BaseModel, ConfigDict
from yarl import URL


class HTTPResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: URL
    status_code: int
    headers: CIMultiDictProxy[str]
    cookies: SimpleCookie


class JSONHTTPResponse(HTTPResponse):
    json_: dict[str, Any]


class TextHTTPResponse(HTTPResponse):
    data: str
