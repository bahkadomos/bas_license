from sqlalchemy.ext.asyncio import AsyncEngine

from core.models.database import Base


async def create_sqlalchemy_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_sqlalchemy_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
