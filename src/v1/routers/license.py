from fastapi import APIRouter, BackgroundTasks, status

from core.enums import Location
from core.schemas import (
    CreateLicenseTaskInSchema,
    CreateLicenseTaskOutSchema,
    ErrorResponse,
    SuccessResponse,
    TaskLicenseResultInSchema,
    TaskLicenseResultOutSchema,
    TaskNotFoundSchema,
)
from v1.dependencies import BasWorkerDependency, TaskUseCaseDependency
from v1.exceptions import NotFoundError

router = APIRouter(prefix="/v1/license")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    background_tasks: BackgroundTasks,
    user: CreateLicenseTaskInSchema,
    bas_client: BasWorkerDependency,
    task_use_case: TaskUseCaseDependency,
) -> SuccessResponse[CreateLicenseTaskOutSchema]:
    data = await task_use_case.create_task(
        background_tasks=background_tasks,
        user=user,
        bas_client=bas_client,
    )
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
    task_use_case: TaskUseCaseDependency,
) -> SuccessResponse[TaskLicenseResultOutSchema]:
    data = await task_use_case.get_task_result(task=task)
    if data is None:
        raise NotFoundError("Task id", loc=Location.body, field="task_id")
    return SuccessResponse(data=data)
