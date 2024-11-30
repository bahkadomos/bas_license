from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    def __repr__(self) -> str:
        columns = [
            f"{col.key}={getattr(self, col.key)}"
            for col in self.__table__.columns
        ]
        return f"{self.__class__.__name__}({', '.join(columns)})"


def get_sqlalchemy_engine(dsn: str, *, debug: bool = False) -> AsyncEngine:
    return create_async_engine(
        dsn, pool_size=10, max_overflow=20, pool_pre_ping=False, echo=debug
    )


def get_sqlalchemy_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
