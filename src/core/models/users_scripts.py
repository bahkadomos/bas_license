from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._types import uuid, uuidpk
from .database import Base

if TYPE_CHECKING:
    from .scripts import ScriptsModel
    from .users import UsersModel


class UsersScriptsModel(Base):
    __tablename__ = "users_scripts"
    __table_args__ = (
        UniqueConstraint("user_id", "script_id", name="uq_user_script"),
    )

    id: Mapped[uuidpk]
    user_id: Mapped[uuid] = mapped_column(ForeignKey("users.id"))
    script_id: Mapped[uuid] = mapped_column(ForeignKey("scripts.id"))

    users: Mapped["UsersModel"] = relationship(back_populates="scripts")
    scripts: Mapped["ScriptsModel"] = relationship(back_populates="users")
