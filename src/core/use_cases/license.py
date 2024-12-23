from datetime import datetime
from typing import Protocol

from core._types import UUIDv4
from core.enums import LicenseResultStatus
from core.services.uow import IUnitOfWork


class ILicenseUseCase(Protocol):
    def __init__(self, uow: IUnitOfWork) -> None: ...

    async def set_license_data(
        self,
        task_data_id: UUIDv4,
        *,
        status: LicenseResultStatus,
        expires_in: datetime | None = None,
        is_expired: bool | None = None,
    ) -> None: ...


class LicenseUseCase:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def set_license_data(
        self,
        task_data_id: UUIDv4,
        *,
        status: LicenseResultStatus,
        expires_in: datetime | None = None,
        is_expired: bool | None = None,
    ) -> None:
        async with self._uow:
            await self._uow.license_tasks_data.add_task_data(
                task_data_id,
                status=status,
                expires_in=expires_in,
                is_expired=is_expired,
            )
            await self._uow.commit()
