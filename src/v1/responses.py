from collections.abc import Mapping

from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask

from core.schemas import ErrorResponse


class GenericErrorResponse[T](JSONResponse):
    def __init__(
        self,
        content: T,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: T) -> bytes:
        return super().render(
            ErrorResponse(data=content).model_dump(mode="json")
        )
