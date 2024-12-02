import asyncio
from typing import Protocol

from core._types import UUIDv4
from core.config import settings
from core.enums import LicenseResultStatus
from core.services.bas import (
    BasAPIClient,
    BasAuthClient,
    LicenseResponseResultSchema,
)
from core.services.recaptcha import BaseRecaptchaClient
from core.services.uow import IUnitOfWork
from core.utils import IHTTPClient


class IBasWorker(Protocol):
    def __init__(
        self,
        *,
        uow: IUnitOfWork,
        http_client: IHTTPClient,
        captcha_client: BaseRecaptchaClient,
    ) -> None: ...

    async def __call__(
        self, task_data_id: UUIDv4, user: str, script: str
    ) -> None: ...


class BasWorker:
    KEY: str
    ENV_SESSION = "BAS_SESSION"

    def __init__(
        self,
        *,
        uow: IUnitOfWork,
        http_client: IHTTPClient,
        captcha_client: BaseRecaptchaClient,
    ) -> None:
        self._auth_client = BasAuthClient(
            http_client=http_client,
            captcha_client=captcha_client,
            username=settings.bas_username,
            password=settings.bas_password,
        )
        self._api_client = BasAPIClient(http_client)
        self._uow = uow
        self._bas_session: str | None = None
        self._session_lock = asyncio.Lock()

    async def __call__(
        self, task_data_id: UUIDv4, user: str, script: str
    ) -> None:
        if self._bas_session is None:
            self._bas_session = await self._get_storage_session()
            await self._ensure_session_update()
        license_data = await self._get_license_data(user, script)
        await self._save_license_data(task_data_id, license_data)

    async def _get_storage_session(self) -> str | None:
        async with self._uow:
            session = await self._uow.sessions.read_one()
            await self._uow.commit()
        return session

    async def _set_storage_session(self) -> None:
        if self._bas_session:
            async with self._uow:
                await self._uow.sessions.create_one(self._bas_session)
                await self._uow.commit()

    def _set_bas_session(self) -> None:
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
        await self._set_storage_session()
        self._set_bas_session()

    async def _save_license_data(
        self, task_data_id: UUIDv4, data: LicenseResponseResultSchema
    ) -> None:
        expires_in = data.credentials.expires_in if data.credentials else None
        is_expired = data.credentials.is_expired if data.credentials else None
        async with self._uow:
            await self._uow.license_tasks_data.add_task_data(
                task_data_id,
                status=data.status,
                expires_in=expires_in,
                is_expired=is_expired,
            )
            await self._uow.commit()
