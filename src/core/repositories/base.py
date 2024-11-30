from typing import Any, Protocol, cast, get_args
from collections.abc import Iterable

from pydantic import BaseModel
from sqlalchemy import CursorResult, Result, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from core._types import DictOrPydantic

from .exceptions import InvalidDataError


class ISQLAlchemyRepository[T](Protocol):
    def as_dict(
        self, data: DictOrPydantic, *, exclude_none: bool = False
    ) -> dict[str, Any]: ...

    async def create(
        self,
        data: DictOrPydantic,
        *,
        returning: Iterable[InstrumentedAttribute[Any]] | None = None,
    ) -> CursorResult: ...

    async def read(
        self,
        *,
        filter_by: DictOrPydantic | None = None,
        order_by: Iterable[_ColumnExpressionArgument[T] | str] | None = None,
        returning: Iterable[InstrumentedAttribute[Any]] | None = None,
    ) -> Result: ...

    async def update(
        self,
        data: DictOrPydantic,
        *,
        where: Iterable[_ColumnExpressionArgument[bool]],
        exclude_none: bool = False,
        returning: Iterable[InstrumentedAttribute[Any]] | None = None,
    ) -> CursorResult: ...


class SQLAlchemyRepository[T]:
    def __init__(self, session: AsyncSession) -> None:
        self.model = cast(type[T], get_args(self.__orig_bases__[0])[0])  # type: ignore
        self.session = session

    def as_dict(
        self, data: DictOrPydantic, *, exclude_none: bool = False
    ) -> dict[str, Any]:
        if isinstance(data, BaseModel):
            return data.model_dump(exclude_none=exclude_none)
        elif isinstance(data, dict):
            if exclude_none:
                data = {k: v for k, v in data.items() if v is not None}
            return data
        else:
            raise InvalidDataError(data)

    async def create(
        self,
        data: DictOrPydantic,
        *,
        returning: Iterable[InstrumentedAttribute[Any]] | None = None,
    ) -> CursorResult:
        stmt = insert(self.model).values(**self.as_dict(data))
        if returning is not None:
            stmt = stmt.returning(*returning)
        return await self.session.execute(stmt)

    async def read(
        self,
        *,
        filter_by: DictOrPydantic | None = None,
        order_by: Iterable[_ColumnExpressionArgument[T] | str] | None = None,
        returning: Iterable[InstrumentedAttribute[Any]] | None = None,
    ) -> Result:
        stmt = select(*returning or (self.model,))
        if filter_by:
            stmt = stmt.filter_by(**self.as_dict(filter_by))
        if order_by:
            stmt = stmt.order_by(*order_by)
        return await self.session.execute(stmt)

    async def update(
        self,
        data: DictOrPydantic,
        *,
        where: Iterable[_ColumnExpressionArgument[bool]],
        exclude_none: bool = False,
        returning: Iterable[InstrumentedAttribute[Any]] | None = None,
    ) -> CursorResult:
        stmt = (
            update(self.model)
            .where(*where)
            .values(**self.as_dict(data, exclude_none=exclude_none))
        )
        if returning is not None:
            stmt = stmt.returning(*returning)
        return await self.session.execute(stmt)
