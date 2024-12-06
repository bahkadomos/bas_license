from typing import Annotated

from fastapi import Depends, Request

from core.utils import IClientSession, IHTTPClient, RetryAiohttpClient

from .logger import LoggerDependency

def get_http_session(request: Request) -> IClientSession:
    return request.app.state.http_session


def get_http_client(
    session: Annotated[IClientSession, Depends(get_http_session)],
    logger: LoggerDependency,
) -> IHTTPClient:
    return RetryAiohttpClient(session, logger)


HTTPClentDependency = Annotated[IHTTPClient, Depends(get_http_client)]
