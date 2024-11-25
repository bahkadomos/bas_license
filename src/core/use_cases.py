from typing import Protocol
from fastapi import BackgroundTasks

from .schemas import (
    CreateLicenseTaskInSchema,
    CreateLicenseTaskOutSchema,
    LicenseDetailsSchema,
    TaskLicenseResultInSchema,
    TaskLicenseResultOutSchema,
)
from .services.uow import IUnitOfWork
from .services.workers import BasWorker


class ITaskUseCase(Protocol):
    def __init__(self, uow: IUnitOfWork) -> None: ...

    async def create_task(
        self,
        background_tasks: BackgroundTasks,
        user: CreateLicenseTaskInSchema,
        bas_client: BasWorker,
    ) -> CreateLicenseTaskOutSchema: ...

    async def get_task_result(
        self, task: TaskLicenseResultInSchema
    ) -> TaskLicenseResultOutSchema | None: ...


class TaskUseCase:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def create_task(
        self,
        background_tasks: BackgroundTasks,
        user: CreateLicenseTaskInSchema,
        bas_client: BasWorker,
    ) -> CreateLicenseTaskOutSchema:
        async with self._uow as uow:
            user_id = await self._uow.users.create_one(user.username)
            script_id = await uow.scripts.create_one(user.script_name)
            user_script_id = await uow.users_scripts.create_one(
                user_id=user_id, script_id=script_id
            )
            task_data_id = await uow.license_tasks_data.create_one()
            task_id = await uow.license_tasks.create_one(
                task_data_id=task_data_id, user_script_id=user_script_id
            )
            await uow.commit()
        background_tasks.add_task(
            bas_client, task_data_id, user.username, user.script_name
        )
        return CreateLicenseTaskOutSchema(task_id=task_id, credentials=user)

    async def get_task_result(
        self, task: TaskLicenseResultInSchema
    ) -> TaskLicenseResultOutSchema | None:
        async with self._uow as uow:
            data = await uow.license_tasks.read_one(task.task_id)
            await uow.commit()
        if data is None:
            return None
        creds = data.task_data
        if (
            creds is None
            or creds.is_expired is None
            or creds.expires_in is None
        ):
            return TaskLicenseResultOutSchema(
                status=creds.status,
            )
        return TaskLicenseResultOutSchema(
            status=creds.status,
            credentials=LicenseDetailsSchema(
                is_expired=creds.is_expired, expires_in=creds.expires_in
            ),
        )
