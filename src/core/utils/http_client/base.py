from http.cookies import SimpleCookie
from logging import Logger
from typing import Any, Literal, Protocol, overload

from aiohttp import ClientSession

from .enums import HTTPResponseType
from .schemas import HTTPResponse, JSONHTTPResponse, TextHTTPResponse


class IHTTPClient(Protocol):
    def __init__(self, session: ClientSession, logger: Logger) -> None: ...

    @overload
    async def request(
        self,
        method: str,
        url: str,
        *,
        response_type: Literal[HTTPResponseType.json],
        **kwargs: Any,
    ) -> JSONHTTPResponse: ...

    @overload
    async def request(
        self,
        method: str,
        url: str,
        *,
        response_type: Literal[HTTPResponseType.text],
        **kwargs: Any,
    ) -> TextHTTPResponse: ...

    @overload
    async def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> JSONHTTPResponse: ...

    async def request(
        self,
        method: str,
        url: str,
        response_type: HTTPResponseType = HTTPResponseType.json,
        **kwargs: Any,
    ) -> HTTPResponse: ...

    @overload
    async def get(
        self,
        url: str,
        *,
        response_type: Literal[HTTPResponseType.json],
        **kwargs: Any,
    ) -> JSONHTTPResponse: ...

    @overload
    async def get(
        self,
        url: str,
        *,
        response_type: Literal[HTTPResponseType.text],
        **kwargs: Any,
    ) -> TextHTTPResponse: ...

    @overload
    async def get(
        self,
        url: str,
        **kwargs: Any,
    ) -> JSONHTTPResponse: ...

    async def get(
        self,
        url: str,
        *,
        response_type: HTTPResponseType = HTTPResponseType.json,
        **kwargs: Any,
    ) -> HTTPResponse: ...

    @overload
    async def post(
        self,
        url: str,
        *,
        response_type: Literal[HTTPResponseType.json],
        **kwargs: Any,
    ) -> JSONHTTPResponse: ...

    @overload
    async def post(
        self,
        url: str,
        *,
        response_type: Literal[HTTPResponseType.text],
        **kwargs: Any,
    ) -> TextHTTPResponse: ...

    @overload
    async def post(
        self,
        url: str,
        **kwargs: Any,
    ) -> JSONHTTPResponse: ...

    async def post(
        self,
        url: str,
        *,
        response_type: HTTPResponseType = HTTPResponseType.json,
        **kwargs: Any,
    ) -> HTTPResponse: ...

    def get_cookie(self) -> SimpleCookie: ...

    def set_cookie(self, cookies: dict[str, str]) -> None: ...
