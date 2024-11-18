from datetime import datetime
from typing import Annotated

from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column

from core._types import UUIDv4

uuid = Annotated[UUIDv4, mapped_column(UUID)]
uq_uuid = Annotated[UUIDv4, mapped_column(UUID, unique=True)]
uuidpk = Annotated[
    UUIDv4,
    mapped_column(
        UUID, primary_key=True, server_default=text("gen_random_uuid()")
    ),
]
str_255 = Annotated[str, mapped_column(String(255))]
date_time = Annotated[datetime, mapped_column(DateTime())]
boolean = Annotated[bool, mapped_column(Boolean())]
created_at = Annotated[
    datetime, mapped_column(server_default=func.current_timestamp())
]
updated_at = Annotated[
    datetime,
    mapped_column(
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    ),
]
