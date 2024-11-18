from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from core._types import UUIDv4
from core.models import LicenseTasksModel

from .base import ISQLAlchemyRepository, SQLAlchemyRepository


class ILicenseTasksRepository(
    ISQLAlchemyRepository[LicenseTasksModel], Protocol
):
    async def create_one(
        self, *, task_data_id: UUIDv4, user_script_id: UUIDv4
    ) -> LicenseTasksModel: ...

    async def read_one(
        self, task_id: UUIDv4, /
    ) -> LicenseTasksModel | None: ...


class SQLAlchemyLicenseTasksRepository(
    SQLAlchemyRepository[LicenseTasksModel]
):
    async def create_one(
        self, *, task_data_id: UUIDv4, user_script_id: UUIDv4
    ) -> LicenseTasksModel:
        res = await self.create(
            dict(task_data_id=task_data_id, user_script_id=user_script_id),
            returning=[self.model.id],
        )
        return res.scalar_one()

    async def read_one(self, task_id: UUIDv4, /) -> LicenseTasksModel | None:
        stmt = (
            select(self.model)
            .filter(self.model.id == task_id)
            .options(joinedload(self.model.task_data))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
