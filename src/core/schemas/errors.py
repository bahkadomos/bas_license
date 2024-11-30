from typing import Annotated

from pydantic import BaseModel, Field

from core.enums import Location


class TaskNotFoundSchema(BaseModel):
    location: Annotated[str, Field(default=Location.body.value)]
    field: Annotated[str, Field(default="task_id")]
    description: Annotated[str, Field(default="Task id not found")]
