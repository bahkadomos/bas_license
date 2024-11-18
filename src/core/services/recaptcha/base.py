from abc import ABC, abstractmethod
from typing import Any

from core.config import CaptchaService, settings
from core.utils import IHTTPClient, exc_wrapper

from .exceptions import RecaptchaError


class BaseRecaptchaClient(ABC):
    registry: dict[CaptchaService, type["BaseRecaptchaClient"]] = {}

    def __init_subclass__(cls, service: CaptchaService, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        cls.registry[service] = cls

    def __init__(
        self,
        *,
        http_client: IHTTPClient
    ) -> None:
        self._client = http_client
        self._attempts = settings.captcha_attempts
        self._delay = settings.captcha_delay

    @exc_wrapper(AssertionError, RecaptchaError)
    async def create_task(self, site_key: str, page_url: str) -> Any:
        return await self._create_task_impl(site_key, page_url)

    @exc_wrapper(AssertionError, RecaptchaError)
    async def get_token(self, task_id: Any) -> str:
        return await self._get_token_impl(task_id)

    @abstractmethod
    async def _create_task_impl(self, site_key: str, page_url: str) -> Any:
        raise NotImplementedError()

    @abstractmethod
    async def _get_token_impl(self, task_id: Any) -> str:
        raise NotImplementedError()


def get_recaptcha_client(http_client: IHTTPClient) -> BaseRecaptchaClient:
    client_class = BaseRecaptchaClient.registry.get(settings.captcha_service)
    if client_class is None:
        raise ValueError(f"Unknown service: {settings.captcha_service}")
    return client_class(http_client=http_client)
