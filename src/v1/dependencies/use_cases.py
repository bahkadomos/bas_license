from typing import Annotated

from fastapi import Depends

from core.use_cases import ITaskUseCase, TaskUseCase

from .uow import UOWDependency


def task_use_case(uow: UOWDependency) -> ITaskUseCase:
    return TaskUseCase(uow)


TaskUseCaseDependency = Annotated[ITaskUseCase, Depends(task_use_case)]
