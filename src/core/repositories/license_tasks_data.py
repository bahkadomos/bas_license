from datetime import datetime
from typing import Protocol

from core._types import UUIDv4
from core.enums import LicenseResultStatus
from core.models import LicenseTasksDataModel

from .base import ISQLAlchemyRepository, SQLAlchemyRepository


class ILicenseTasksDataRepository(
    ISQLAlchemyRepository[LicenseTasksDataModel], Protocol
):
    async def create_one(self) -> UUIDv4: ...

    async def add_task_data(
        self,
        task_data_id: UUIDv4,
        *,
        status: LicenseResultStatus,
        expires_in: datetime | None = None,
        is_expired: bool | None = None,
    ) -> UUIDv4 | None: ...


class SQLAlchemyLicenseTasksDataRepository(
    SQLAlchemyRepository[LicenseTasksDataModel]
):
    async def create_one(self) -> UUIDv4:
        res = await self.create(dict(), returning=[self.model.id])
        return res.scalar_one()

    async def add_task_data(
        self,
        task_data_id: UUIDv4,
        *,
        status: LicenseResultStatus,
        expires_in: datetime | None = None,
        is_expired: bool | None = None,
    ) -> UUIDv4 | None:
        res = await self.update(
            dict(status=status, expires_in=expires_in, is_expired=is_expired),
            where=[self.model.id == task_data_id],
            exclude_none=True,
            returning=[self.model.id],
        )
        return res.scalar_one_or_none()
