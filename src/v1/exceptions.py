from fastapi import HTTPException, status

from core import constants
from core.enums import Location


class NotFoundError(HTTPException):
    def __init__(
        self, item: str, loc: Location, field: str | None = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=constants.NOT_FOUND.format(item=item.capitalize()),
        )
        self.loc = loc
        self.field = field
