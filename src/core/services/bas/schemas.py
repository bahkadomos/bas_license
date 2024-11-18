from pydantic import BaseModel

from core.enums import LicenseResultStatus
from core.schemas import LicenseDetailsSchema


class LicenseResponseResultSchema(BaseModel):
    status: LicenseResultStatus
    credentials: LicenseDetailsSchema | None = None
