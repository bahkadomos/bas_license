from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._types import created_at, str_255, uuidpk
from .database import Base

if TYPE_CHECKING:
    from .users_scripts import UsersScriptsModel


class UsersModel(Base):
    __tablename__ = "users"

    id: Mapped[uuidpk]
    username: Mapped[str_255] = mapped_column(unique=True)
    created_at: Mapped[created_at]

    scripts: Mapped[list["UsersScriptsModel"]] = relationship(
        back_populates="users"
    )
