from typing import Annotated

from fastapi import Depends

from core.services.workers import BasWorker, IBasWorker

from .captcha import CaptchaClientDependency
from .http_client import HTTPClentDependency
from .logger import LoggerDependency
from .uow import UOWDependency


async def get_bas_worker(
    uow: UOWDependency,
    http_client: HTTPClentDependency,
    captcha_client: CaptchaClientDependency,
    logger: LoggerDependency,
) -> IBasWorker:
    return BasWorker(
        uow=uow,
        http_client=http_client,
        captcha_client=captcha_client,
        logger=logger,
    )


BasWorkerDependency = Annotated[IBasWorker, Depends(get_bas_worker)]
