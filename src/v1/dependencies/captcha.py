from typing import Annotated

from fastapi import Depends

from core.services.recaptcha import BaseRecaptchaClient, get_recaptcha_client

from .http_client import HTTPClentDependency
from .logger import LoggerDependency


def get_captcha_client(
    http_client: HTTPClentDependency,
    logger: LoggerDependency,
) -> BaseRecaptchaClient:
    return get_recaptcha_client(http_client=http_client, logger=logger)


CaptchaClientDependency = Annotated[
    BaseRecaptchaClient, Depends(get_captcha_client)
]
