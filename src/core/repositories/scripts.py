from typing import Protocol

from sqlalchemy.dialects.postgresql import insert

from core._types import UUIDv4
from core.models import ScriptsModel

from .base import ISQLAlchemyRepository, SQLAlchemyRepository


class IScriptsRepository(ISQLAlchemyRepository[ScriptsModel], Protocol):
    async def create_one(self, script_name: str, /) -> UUIDv4: ...


class SQLAlchemyScriptsRepository(SQLAlchemyRepository[ScriptsModel]):
    async def create_one(self, script_name: str, /) -> UUIDv4:
        insert_stmt = insert(self.model).values(script_name=script_name)
        stmt = insert_stmt.on_conflict_do_update(
            index_elements=[self.model.script_name],
            set_=dict(script_name=insert_stmt.excluded.script_name),
        ).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()
