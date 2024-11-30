from typing import Any
from uuid import UUID

from pydantic import BaseModel

type UUIDv4 = UUID
type DictOrPydantic = dict[str, Any] | BaseModel
