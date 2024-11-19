from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from core.enums import LicenseResultStatus

from ._types import boolean, created_at, date_time, updated_at, uuidpk
from .database import Base


class LicenseTasksDataModel(Base):
    __tablename__ = "license_tasks_data"

    id: Mapped[uuidpk]
    status: Mapped[LicenseResultStatus] = mapped_column(
        Enum(
            LicenseResultStatus,
            name="license_status",
            create_constraint=True,
            validate_strings=True,
        ),
        server_default=LicenseResultStatus.pending.value,
    )
    expires_in: Mapped[date_time | None]
    is_expired: Mapped[boolean | None]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
