import base64

from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from core.config import settings

from .utils import EncryptionMixin


class EncryptionMiddleware(BaseHTTPMiddleware, EncryptionMixin):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)
        if (
            response.status_code < HTTP_500_INTERNAL_SERVER_ERROR
            and request.method in ("POST", "PUT", "PATCH")
        ):
            body = [section async for section in response.body_iterator]  # type: ignore
            response.body_iterator = iterate_in_threadpool(iter(body))  # type: ignore

            priv_key = super().serialize_pem_private_key(settings.private_key)
            digest = super().get_sha256_hash(body[0])
            signature = super().get_signature(priv_key, digest)
            response.headers["X-Signature"] = base64.b64encode(
                signature
            ).decode()

        return response
