from fastapi import APIRouter, BackgroundTasks, status

from core.enums import Location
from core.schemas import (
    CreateLicenseTaskInSchema,
    CreateLicenseTaskOutSchema,
    ErrorResponse,
    LicenseDetailsSchema,
    SuccessResponse,
    TaskLicenseResultInSchema,
    TaskLicenseResultOutSchema,
    TaskNotFoundSchema,
)
from v1.dependencies import BasWorkerDependency, UOWDependency
from v1.exceptions import NotFoundError

router = APIRouter(prefix="/v1/license")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    background_tasks: BackgroundTasks,
    user: CreateLicenseTaskInSchema,
    uow: UOWDependency,
    bas_client: BasWorkerDependency,
) -> SuccessResponse[CreateLicenseTaskOutSchema]:
    async with uow:
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
    background_tasks.add_task(
        bas_client, task_data_id, user.username, user.script_name
    )
    data = CreateLicenseTaskOutSchema(task_id=task_id, credentials=user)
    return SuccessResponse(data=data)


@router.post(
    "/result/",
    responses={
        status.HTTP_404_NOT_FOUND: dict(
            model=ErrorResponse[TaskNotFoundSchema],
            description="Task id not found",
        )
    },
)
async def get_task_result(
    task: TaskLicenseResultInSchema,
    uow: UOWDependency,
) -> SuccessResponse[TaskLicenseResultOutSchema]:
    async with uow:
        data = await uow.license_tasks.read_one(task.task_id)
        await uow.commit()
    if data is None:
        raise NotFoundError("Task id", loc=Location.body, field="task_id")
    creds = data.task_data
    if creds is None or creds.is_expired is None or creds.expires_in is None:
        res = TaskLicenseResultOutSchema(
            status=creds.status,
        )
        return SuccessResponse(data=res)
    res = TaskLicenseResultOutSchema(
        status=creds.status,
        credentials=LicenseDetailsSchema(
            is_expired=creds.is_expired, expires_in=creds.expires_in
        ),
    )
    return SuccessResponse(data=res)
