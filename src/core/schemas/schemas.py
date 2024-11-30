from datetime import datetime

from pydantic import BaseModel

from core._types import UUIDv4
from core.enums import LicenseResultStatus


class CreateLicenseTaskInSchema(BaseModel):
    username: str
    script_name: str


class CreateLicenseTaskOutSchema(BaseModel):
    task_id: UUIDv4
    credentials: CreateLicenseTaskInSchema


class LicenseDetailsSchema(BaseModel):
    is_expired: bool
    expires_in: datetime


class TaskLicenseResultInSchema(BaseModel):
    task_id: UUIDv4


class TaskLicenseResultOutSchema(BaseModel):
    status: LicenseResultStatus
    credentials: LicenseDetailsSchema | None = None
