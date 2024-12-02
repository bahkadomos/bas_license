from sqlalchemy import Boolean, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import true

from ._types import created_at, updated_at
from .database import Base


class SessionsModel(Base):
    __tablename__ = "sessions"
    __table_args__ = (CheckConstraint("id = TRUE", name="onerow_unq"),)

    id: Mapped[bool] = mapped_column(
        Boolean, primary_key=True, server_default=true(), nullable=False
    )
    session: Mapped[str] = mapped_column(String())
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
