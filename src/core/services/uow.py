from types import TracebackType
from typing import Protocol, Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.repositories import (
    ILicenseTasksDataRepository,
    ILicenseTasksRepository,
    IScriptsRepository,
    ISessionsRepository,
    IUsersRepository,
    IUsersScriptsRepository,
    SQLAlchemyLicenseTasksDataRepository,
    SQLAlchemyLicenseTasksRepository,
    SQLAlchemyScriptsRepository,
    SQLAlchemySessionsRepository,
    SQLAlchemyUsersRepository,
    SQLAlchemyUsersScriptsRepository,
)


class IUnitOfWork(Protocol):
    @property
    def license_tasks(self) -> ILicenseTasksRepository: ...

    @property
    def license_tasks_data(self) -> ILicenseTasksDataRepository: ...

    @property
    def scripts(self) -> IScriptsRepository: ...

    @property
    def sessions(self) -> ISessionsRepository: ...

    @property
    def users(self) -> IUsersRepository: ...

    @property
    def users_scripts(self) -> IUsersScriptsRepository: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...


class UnitOfWork:
    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        self._session_factory = session_factory

    @property
    def license_tasks(self) -> ILicenseTasksRepository:
        return SQLAlchemyLicenseTasksRepository(self._session)

    @property
    def license_tasks_data(self) -> ILicenseTasksDataRepository:
        return SQLAlchemyLicenseTasksDataRepository(self._session)

    @property
    def scripts(self) -> IScriptsRepository:
        return SQLAlchemyScriptsRepository(self._session)

    @property
    def sessions(self) -> ISessionsRepository:
        return SQLAlchemySessionsRepository(self._session)

    @property
    def users(self) -> IUsersRepository:
        return SQLAlchemyUsersRepository(self._session)

    @property
    def users_scripts(self) -> IUsersScriptsRepository:
        return SQLAlchemyUsersScriptsRepository(self._session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def _close(self) -> None:
        await self._session.close()

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.rollback()
        await self._close()
