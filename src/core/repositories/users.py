from typing import Protocol

from sqlalchemy.dialects.postgresql import insert

from core._types import UUIDv4
from core.models import UsersModel

from .base import ISQLAlchemyRepository, SQLAlchemyRepository


class IUsersRepository(ISQLAlchemyRepository[UsersModel], Protocol):
    async def create_one(self, username: str, /) -> UUIDv4: ...


class SQLAlchemyUsersRepository(SQLAlchemyRepository[UsersModel]):
    async def create_one(self, username: str, /) -> UUIDv4:
        insert_stmt = insert(self.model).values(username=username)
        stmt = insert_stmt.on_conflict_do_update(
            index_elements=[self.model.username],
            set_=dict(username=insert_stmt.excluded.username),
        ).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()
