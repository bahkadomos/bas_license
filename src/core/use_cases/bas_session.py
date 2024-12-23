from typing import Protocol

from core.services.uow import IUnitOfWork


class IBASSessionUseCase(Protocol):
    def __init__(self, uow: IUnitOfWork) -> None: ...

    async def get_session(self) -> str | None: ...

    async def set_session(self, session: str) -> None: ...


class BASSessionUseCase:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def get_session(self) -> str | None:
        async with self._uow:
            session = await self._uow.sessions.read_one()
            await self._uow.commit()
        return session

    async def set_session(self, session: str) -> None:
        async with self._uow:
            await self._uow.sessions.create_one(session)
            await self._uow.commit()
