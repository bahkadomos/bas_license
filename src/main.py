from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from prometheus_fastapi_instrumentator import Instrumentator

from core.config import settings
from core.models import get_sqlalchemy_engine
from core.schemas import ErrorDetailsSchema, ErrorResponse
from core.utils import get_client_session, get_loki_logger, get_null_logger
from v1.handlers import http_exception_handler, request_validation_handler
from v1.middlewares import EncryptionMiddleware
from v1.routers import license


def create_app(enable_monitoring: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.engine = get_sqlalchemy_engine(settings.dsn)
        app.state.http_session = get_client_session(timeout=30)
        if enable_monitoring:
            app.state.logger = get_loki_logger()
        else:
            app.state.logger = get_null_logger()

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
    if enable_monitoring:
        Instrumentator(
            should_instrument_requests_inprogress=True,
            should_group_status_codes=False,
            excluded_handlers=["/docs", "/openapi.json", "/metrics"],
        ).instrument(app).expose(app)

    return app


app = create_app()
