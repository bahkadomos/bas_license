from typing import Protocol

from core.schemas import (
    CreateLicenseTaskInSchema,
    CreateLicenseTaskOutSchema,
    LicenceTaskUseCaseOut,
    LicenseDetailsSchema,
    TaskLicenseResultInSchema,
    TaskLicenseResultOutSchema,
)
from core.services.uow import IUnitOfWork


class ITaskUseCase(Protocol):
    def __init__(self, uow: IUnitOfWork) -> None: ...

    async def create_task(
        self,
        user: CreateLicenseTaskInSchema,
    ) -> LicenceTaskUseCaseOut: ...

    async def get_task_result(
        self, task: TaskLicenseResultInSchema
    ) -> TaskLicenseResultOutSchema | None: ...


class TaskUseCase:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def create_task(
        self,
        user: CreateLicenseTaskInSchema,
    ) -> LicenceTaskUseCaseOut:
        async with self._uow as uow:
            user_id = await uow.users.create_one(user.username)
            script_id = await uow.scripts.create_one(user.script_name)
            user_script_id = await uow.users_scripts.create_one(
                user_id=user_id, script_id=script_id
            )
            task_data_id = await uow.license_tasks_data.create_one()
            task_id = await uow.license_tasks.create_one(
                task_data_id=task_data_id, user_script_id=user_script_id
            )
            await uow.commit()
        return LicenceTaskUseCaseOut(
            response_data=CreateLicenseTaskOutSchema(
                task_id=task_id, credentials=user
            ),
            task_data_id=task_data_id,
        )

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
                is_expired=creds.is_expired,
                expires_in=creds.expires_in
            ),
        )
