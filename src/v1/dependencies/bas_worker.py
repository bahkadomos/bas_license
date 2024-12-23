from typing import Annotated

from fastapi import Depends

from core.services.workers import BasWorker, IBasWorker

from .captcha import CaptchaClientDependency
from .http_client import HTTPClentDependency
from .logger import LoggerDependency
from .use_cases import IBASSessionUseCase, ILicenseUseCase


async def get_bas_worker(
    bas_session_use_case: IBASSessionUseCase,
    license_use_case: ILicenseUseCase,
    http_client: HTTPClentDependency,
    captcha_client: CaptchaClientDependency,
    logger: LoggerDependency,
) -> IBasWorker:
    return BasWorker(
        bas_session_use_case=bas_session_use_case,
        license_use_case=license_use_case,
        http_client=http_client,
        captcha_client=captcha_client,
        logger=logger,
    )


BasWorkerDependency = Annotated[IBasWorker, Depends(get_bas_worker)]
