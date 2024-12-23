from pydantic import BaseModel

from core._types import UUIDv4

from .schemas import CreateLicenseTaskOutSchema


class LicenceTaskUseCaseOut(BaseModel):
    response_data: CreateLicenseTaskOutSchema
    task_data_id: UUIDv4
