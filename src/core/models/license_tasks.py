from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._types import created_at, updated_at, uq_uuid, uuidpk
from .database import Base

if TYPE_CHECKING:
    from .license_tasks_data import LicenseTasksDataModel


class LicenseTasksModel(Base):
    __tablename__ = "license_tasks"

    id: Mapped[uuidpk]
    user_script_id: Mapped[uq_uuid] = mapped_column(
        ForeignKey("users_scripts.id", ondelete="CASCADE"), unique=False
    )
    task_data_id: Mapped[uq_uuid] = mapped_column(
        ForeignKey("license_tasks_data.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    task_data: Mapped["LicenseTasksDataModel"] = relationship()
