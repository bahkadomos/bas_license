from typing import Annotated

from fastapi import Depends, Request

from core.models import get_sqlalchemy_session_factory
from core.services.uow import IUnitOfWork, UnitOfWork


def get_uow(request: Request) -> IUnitOfWork:
    session_factory = get_sqlalchemy_session_factory(request.app.state.engine)
    return UnitOfWork(session_factory)


UOWDependency = Annotated[IUnitOfWork, Depends(get_uow)]
