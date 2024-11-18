from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError

from core.config import settings
from core.models import (
    create_sqlalchemy_tables,
    get_sqlalchemy_engine,
)
from core.schemas import ErrorDetailsSchema, ErrorResponse
from core.utils import get_client_session
from v1.handlers import http_exception_handler, request_validation_handler
from v1.middlewares import EncryptionMiddleware
from v1.routers import license


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.engine = get_sqlalchemy_engine(settings.dsn)
        app.state.http_session = get_client_session()
        await create_sqlalchemy_tables(app.state.engine)

        yield

        await app.state.engine.dispose()
        await app.state.http_session.close()

    app = FastAPI(
        title="BAS License API",
        version="1.0.0",
        lifespan=lifespan,
        responses={
            status.HTTP_422_UNPROCESSABLE_ENTITY: dict(
                model=ErrorResponse[ErrorDetailsSchema],
                description="Validation Error",
            )
        },
        debug=settings.debug,
    )
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(
        RequestValidationError, request_validation_handler
    )
    app.add_middleware(EncryptionMiddleware)
    app.include_router(license.router)

    return app


app = create_app()
