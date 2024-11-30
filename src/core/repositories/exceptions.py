from typing import Any


class RepositoryError(Exception): ...


class InvalidDataError(RepositoryError):
    def __init__(self, data: Any) -> None:
        super().__init__(
            f"Invalid data, expected dict or Pydantic model, got {type(data)}"
        )
