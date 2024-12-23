import asyncio
from logging import Logger
from typing import Protocol

from core._types import UUIDv4
from core.config import settings
from core.enums import LicenseResultStatus
from core.services.bas import (
    BasAPIClient,
    BasAuthClient,
)
from core.services.bas.schemas import LicenseResponseResultSchema
from core.services.recaptcha import BaseRecaptchaClient
from core.use_cases import IBASSessionUseCase, ILicenseUseCase
from core.utils import IHTTPClient


class IBasWorker(Protocol):
    def __init__(
        self,
        *,
        bas_session_use_case: IBASSessionUseCase,
        license_use_case: ILicenseUseCase,
        http_client: IHTTPClient,
        captcha_client: BaseRecaptchaClient,
        logger: Logger,
    ) -> None: ...

    async def __call__(
        self, task_data_id: UUIDv4, user: str, script: str
    ) -> None: ...


class BasWorker:
    ENV_SESSION = "BAS_SESSION"

    def __init__(
        self,
        *,
        bas_session_use_case: IBASSessionUseCase,
        license_use_case: ILicenseUseCase,
        http_client: IHTTPClient,
        captcha_client: BaseRecaptchaClient,
        logger: Logger,
    ) -> None:
        self._auth_client = BasAuthClient(
            http_client=http_client,
            captcha_client=captcha_client,
            username=settings.bas_username,
            password=settings.bas_password,
            logger=logger,
        )
        self._license_use_case = license_use_case
        self._bas_session_use_case = bas_session_use_case
        self._api_client = BasAPIClient(http_client, logger)
        self._bas_session: str | None = None
        self._session_lock = asyncio.Lock()

    async def __call__(
        self, task_data_id: UUIDv4, user: str, script: str
    ) -> None:
        if self._bas_session is None:
            self._bas_session = await self._bas_session_use_case.get_session()
            await self._ensure_session_update()
        license_data = await self._get_license_data(user, script)
        await self._save_license_data(task_data_id, license_data)

    def _set_bas_session(self) -> None:
        if self._bas_session:
            self._api_client.set_session_cookie(self._bas_session)

    async def _get_license_data(
        self, user: str, script: str
    ) -> LicenseResponseResultSchema:
        license_data = await self._api_client.get_user_license(
            user, script
        )
        if self._needs_session_update(license_data):
            self._bas_session = None
            await self._ensure_session_update()
            license_data = await self._api_client.get_user_license(
                user, script
            )
        return license_data

    def _needs_session_update(
        self, license_data: LicenseResponseResultSchema
    ) -> bool:
        return license_data.status == LicenseResultStatus.not_authorized

    async def _ensure_session_update(self) -> None:
        async with self._session_lock:
            if self._bas_session is None:
                await self._update_session()

    async def _update_session(self) -> None:
        self._bas_session = await self._auth_client.get_session_cookie()
        if self._bas_session:
            await self._bas_session_use_case.set_session(self._bas_session)
        self._set_bas_session()

    async def _save_license_data(
        self, task_data_id: UUIDv4, data: LicenseResponseResultSchema
    ) -> None:
        expires_in = data.credentials.expires_in if data.credentials else None
        is_expired = data.credentials.is_expired if data.credentials else None
        await self._license_use_case.set_license_data(
            task_data_id,
            status=data.status,
            expires_in=expires_in,
            is_expired=is_expired,
        )
