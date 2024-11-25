from typing import Annotated

from aiohttp import ClientSession
from fastapi import Depends, Request

from core.models import get_sqlalchemy_session_factory
from core.services.recaptcha import BaseRecaptchaClient, get_recaptcha_client
from core.services.uow import IUnitOfWork, UnitOfWork
from core.services.workers import BasWorker
from core.use_cases import ITaskUseCase, TaskUseCase
from core.utils import IHTTPClient, RetryAiohttpClient


def get_uow(request: Request) -> IUnitOfWork:
    session_factory = get_sqlalchemy_session_factory(request.app.state.engine)
    return UnitOfWork(session_factory)


UOWDependency = Annotated[IUnitOfWork, Depends(get_uow)]


def get_http_session(request: Request) -> ClientSession:
    return request.app.state.http_session


def get_http_client(
    session: Annotated[ClientSession, Depends(get_http_session)],
) -> IHTTPClient:
    return RetryAiohttpClient(session)


HTTPClentDependency = Annotated[IHTTPClient, Depends(get_http_client)]


def get_captcha_client(
    http_client: HTTPClentDependency,
) -> BaseRecaptchaClient:
    return get_recaptcha_client(http_client=http_client)


async def get_bas_worker(
    uow: UOWDependency,
    http_client: HTTPClentDependency,
    captcha_client: Annotated[
        BaseRecaptchaClient, Depends(get_captcha_client)
    ],
) -> BasWorker:
    return BasWorker(
        uow=uow,
        http_client=http_client,
        captcha_client=captcha_client,
    )


BasWorkerDependency = Annotated[BasWorker, Depends(get_bas_worker)]


def task_use_case(uow: UOWDependency) -> ITaskUseCase:
    return TaskUseCase(uow)


TaskUseCaseDependency = Annotated[ITaskUseCase, Depends(task_use_case)]
