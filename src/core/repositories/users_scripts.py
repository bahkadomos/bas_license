from typing import Protocol

from sqlalchemy.dialects.postgresql import insert

from core._types import UUIDv4
from core.models import UsersScriptsModel

from .base import ISQLAlchemyRepository, SQLAlchemyRepository


class IUsersScriptsRepository(
    ISQLAlchemyRepository[UsersScriptsModel], Protocol
):
    async def create_one(
        self, *, user_id: UUIDv4, script_id: UUIDv4
    ) -> UUIDv4: ...


class SQLAlchemyUsersScriptsRepository(
    SQLAlchemyRepository[UsersScriptsModel]
):
    async def create_one(
        self, *, user_id: UUIDv4, script_id: UUIDv4
    ) -> UUIDv4:
        insert_stmt = insert(self.model).values(
            user_id=user_id, script_id=script_id
        )
        stmt = insert_stmt.on_conflict_do_update(
            index_elements=[self.model.user_id, self.model.script_id],
            set_=dict(
                user_id=insert_stmt.excluded.user_id,
                script_id=insert_stmt.excluded.script_id,
            ),
        ).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()
