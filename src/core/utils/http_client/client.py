import json
from http.cookies import SimpleCookie
from logging import Logger
from types import TracebackType
from typing import Any, Literal, Self, cast, overload

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp_retry import ExponentialRetry, RetryClient, RetryOptionsBase

from core.enums import LoggerCallerTypes

from .enums import HTTPResponseType
from .exceptions import HTTPError
from .schemas import HTTPResponse, JSONHTTPResponse, TextHTTPResponse
from .session import IClientSession


class SingleRetryClient(RetryClient):
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        pass


class HTTPRetryClientBuilder:
    def __init__(self) -> None:
        self._retry_option_class: RetryOptionsBase | None = None
        self._raise_for_status = False

    def session(self, __value: IClientSession, /) -> Self:
        """Add instance of `aiohttp.ClientSession`."""
        self._client_session = cast(ClientSession, __value)
        return self

    def options_class(
        self, __value: RetryOptionsBase | None = None, /
    ) -> Self:
        """
        Add class that implements `aiohttp_retry.RetryOptionsBase` class.
        Method is required.
        """
        self._retry_option_class = __value
        return self

    def raise_for_status(self, __value: bool = False, /) -> Self:
        """Add `raise_for_status` param for `RetryClient` constructor."""
        self._raise_for_status = __value
        return self

    def build(self) -> SingleRetryClient:
        return SingleRetryClient(
            client_session=self._client_session,
            retry_options=self._retry_option_class,
            raise_for_status=self._raise_for_status,
        )


class RetryAiohttpClient:
    def __init__(self, session: IClientSession, logger: Logger) -> None:
        builder = HTTPRetryClientBuilder()
        retry_options = ExponentialRetry()
        self._client = (
            builder
            .session(session)
            .options_class(retry_options)
            .build()
        )
        self._logger = logger

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
        *,
        response_type: HTTPResponseType = HTTPResponseType.json,
        **kwargs: Any,
    ) -> HTTPResponse:
        try:
            async with self._client.request(method, url, **kwargs) as response:
                data = await response.text()
                self._cookies = response.cookies
                response_data = dict(
                    url=response.real_url,
                    status_code=response.status,
                    headers=response.headers,
                    cookies=self._cookies,
                )
                if response_type == HTTPResponseType.json:
                    return JSONHTTPResponse(
                        json_=json.loads(data), **response_data
                    )
                elif response_type == HTTPResponseType.text:
                    return TextHTTPResponse(data=data, **response_data)
        except ClientError as e:
            extra = dict(caller=LoggerCallerTypes.http_error.value)
            if isinstance(e, ClientResponseError):
                extra.update(dict(
                    response_url=response.real_url,
                    response_status_code=response.status,
                ))
            self._logger.error("HTTP error", exc_info=e, extra=dict(
                method=method,
                request_url=url,
                **extra,
            ))
            raise HTTPError(e.args[0]) from e

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
    ) -> HTTPResponse:
        return await self.request(
            "GET", url, response_type=response_type, **kwargs
        )

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
    ) -> HTTPResponse:
        return await self.request(
            "POST", url, response_type=response_type, **kwargs
        )

    def get_cookie(self) -> SimpleCookie:
        return getattr(self, "_cookies", None) or SimpleCookie()

    def set_cookie(self, cookies: dict[str, str]) -> None:
        self._client._client.cookie_jar.update_cookies(cookies)
