import time
from typing import Any, Protocol

from aiohttp import (
    ClientResponse,
    ClientResponseError,
    ClientSession,
    ClientTimeout,
)
from aiohttp.typedefs import StrOrURL

from core.services.metrics import (
    OUTGOING_REQUEST_COUNT,
    OUTGOING_REQUEST_LATENCY,
    OUTGOING_REQUESTS_IN_PROGRESS,
)

from .constants import HEADERS


class IClientSession(Protocol):
    async def request(
        self, method: str, str_or_url: StrOrURL, **kwargs: Any
    ) -> ClientResponse: ...

    async def close(self) -> None: ...


class InstrumentedClientSession:
    """Collect metrics for prometheus client"""

    def __init__(self, *args: Any, **kwargs: Any):
        self._session = ClientSession(*args, **kwargs)

    async def request(
        self, method: str, str_or_url: StrOrURL, **kwargs: Any
    ) -> ClientResponse:
        endpoint = (
            str_or_url
            if isinstance(str_or_url, str)
            else str_or_url.human_repr()
        )
        OUTGOING_REQUESTS_IN_PROGRESS.labels(
            method=method, endpoint=endpoint
        ).inc()
        start_time = time.monotonic()
        status_code = 0
        try:
            response = await self._session._request(
                method, str_or_url, **kwargs
            )
            status_code = response.status
            return response
        except ClientResponseError as e:
            status_code = e.status
            raise
        finally:
            elapsed_time = time.monotonic() - start_time
            OUTGOING_REQUEST_COUNT.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()
            OUTGOING_REQUEST_LATENCY.labels(
                method=method, endpoint=endpoint
            ).observe(elapsed_time)
            OUTGOING_REQUESTS_IN_PROGRESS.labels(
                method=method, endpoint=endpoint
            ).dec()

    async def close(self) -> None:
        await self._session.close()

    def __getattr__(self, __name: str, /) -> Any:
        return getattr(self._session, __name)


def get_client_session(
    timeout: float | None = None,
) -> IClientSession:
    client_timeout = ClientTimeout(timeout)
    return InstrumentedClientSession(timeout=client_timeout, headers=HEADERS)
