from typing import Protocol

from sqlalchemy.dialects.postgresql import insert

from core.models import SessionsModel

from .base import ISQLAlchemyRepository, SQLAlchemyRepository


class ISessionsRepository(ISQLAlchemyRepository[SessionsModel], Protocol):
    async def create_one(self, session: str, /) -> str: ...

    async def read_one(self) -> str | None: ...


class SQLAlchemySessionsRepository(SQLAlchemyRepository[SessionsModel]):
    async def create_one(self, session: str, /) -> str:
        insert_stmt = insert(self.model).values(session=session)
        stmt = insert_stmt.on_conflict_do_update(
            index_elements=[self.model.id],
            set_=dict(session=insert_stmt.excluded.session),
        ).returning(self.model.session)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def read_one(self) -> str | None:
        res = await self.read(returning=[self.model.session])
        return res.scalar_one_or_none()
