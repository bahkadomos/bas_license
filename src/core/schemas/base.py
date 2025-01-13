from time import time
import uuid
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from core._types import UUIDv4


class ServerInfoSchema(BaseModel):
    request_id: UUIDv4
    created_at: int

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        if "request_id" not in data:
            data["request_id"] = uuid.uuid4()
        if "created_at" not in data:
            data["created_at"] = int(time() * 1000)
        return data


class ResponseWrapperSchema[T](BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    error: bool
    data: T
    server_info: ServerInfoSchema = Field(default_factory=ServerInfoSchema)  # type: ignore


class SuccessResponse[T](ResponseWrapperSchema[T]):
    model_config = ConfigDict(populate_by_name=True)
    error: bool = False


class ErrorResponse[T](ResponseWrapperSchema[T]):
    model_config = ConfigDict(populate_by_name=True)
    error: bool = True
    data: T


class ErrorDetailsSchema(BaseModel):
    location: Annotated[str | None, Field(default=None)]
    field: Annotated[str | None, Field(default=None)]
    description: str
