from typing import Annotated

from fastapi import Depends

from core.use_cases import (
    BASSessionUseCase,
    IBASSessionUseCase,
    ILicenseUseCase,
    ITaskUseCase,
    LicenseUseCase,
    TaskUseCase,
)

from .uow import UOWDependency


def bas_session_use_case(uow: UOWDependency) -> IBASSessionUseCase:
    return BASSessionUseCase(uow)


BASSessionUseCaseDependency = Annotated[
    IBASSessionUseCase, Depends(bas_session_use_case)
]


def license_use_case(uow: UOWDependency) -> ILicenseUseCase:
    return LicenseUseCase(uow)


LicenseUseCaseDependency = Annotated[
    ILicenseUseCase, Depends(license_use_case)
]


def task_use_case(uow: UOWDependency) -> ITaskUseCase:
    return TaskUseCase(uow)


TaskUseCaseDependency = Annotated[ITaskUseCase, Depends(task_use_case)]
