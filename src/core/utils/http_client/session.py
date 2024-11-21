import time

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


class InstrumentedClientSession(ClientSession):
    '''Collect metrics for prometheus client'''
    async def _request(
        self, method: str, str_or_url: StrOrURL, **kwargs
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
            response = await super()._request(method, str_or_url, **kwargs)
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


def get_client_session(timeout: float | None = None) -> ClientSession:
    client_timeout = ClientTimeout(timeout)
    return InstrumentedClientSession(timeout=client_timeout, headers=HEADERS)
