from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated, Any

from pydantic import Field, computed_field
import pytest
from aiohttp import ClientSession, web
from aiohttp.test_utils import TestClient, TestServer
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
)

from core.config import Settings
from core.models import (
    create_sqlalchemy_tables,
    drop_sqlalchemy_tables,
    get_sqlalchemy_engine,
)
from core.services.bas import BasAPIClient, BasAuthClient
from core.services.recaptcha import (
    BaseRecaptchaClient,
    CapguruRecaptchaClient,
    CapmonsterRecaptchaClient,
)
from core.services.uow import IUnitOfWork, UnitOfWork
from core.utils import EnvManager, RetryAiohttpClient
from core.utils.http_client.client import SingleRetryClient
from v1.dependencies import get_bas_worker, get_http_client

from .helpers import App


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    yield


@dataclass(kw_only=True)
class AppClient:
    client: AsyncClient
    engine: AsyncEngine


@dataclass(kw_only=True)
class AiohttpClientEndpoint:
    router: str
    handler: str
    method: str


class AppSettings(Settings):
    postgres_test_db: Annotated[str, Field(alias="POSTGRES_TEST_DB")]

    @computed_field
    @property
    def test_dsn(self) -> str:
        return ("postgresql+asyncpg://"
                f"{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}"
                f"/{self.postgres_test_db}")


class MemoryManager(EnvManager):
    def __init__(self):
        self._data = dict()

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value


class AiohttpClient(RetryAiohttpClient):
    def __init__(
        self,
        http_client: TestClient,
        client_session: ClientSession,
    ) -> None:
        super().__init__(client_session)
        self._client = SingleRetryClient(client_session=http_client)

    def set_cookie(self, cookies: dict[str, str]) -> None:
        self._client._client.session.cookie_jar.update_cookies(cookies)


@pytest.fixture(autouse=True)
def mock_env_manager(mocker: MockerFixture) -> None:
    mocker.patch(
        "core.services.workers.bas_worker.EnvManager",
        new=MemoryManager,
    )


@pytest.fixture(autouse=True)
def mock_urls(mocker: MockerFixture) -> None:
    objects = [
        BasAPIClient,
        BasAuthClient,
        CapguruRecaptchaClient,
        CapmonsterRecaptchaClient,
    ]
    for obj in objects:
        mocker.patch.object(obj, "BASE_URL", "{}")


@pytest.fixture(autouse=True)
def mock_yarl(mocker: MockerFixture) -> None:
    mocker.patch("yarl.URL.human_repr", new=lambda obj: obj.path)


@pytest.fixture(autouse=True)
def mock_bas_auth_client(mocker: MockerFixture) -> None:
    mocker.patch(
        "core.services.workers.bas_worker.BasAuthClient._get_recaptcha_site_key",
        return_value="test_site_key",
    )
    mocker.patch(
        "core.services.workers.bas_worker.BasAuthClient._get_auth_error",
        return_value=None,
    )


@pytest.fixture(scope="module")
def settings() -> AppSettings:
    return AppSettings()


@pytest.fixture(scope="module")
def dsn(settings: AppSettings) -> str:
    return settings.test_dsn


@pytest.fixture(scope="module")
async def aiohttp_client() -> (
    AsyncGenerator[Callable[[web.Application], Awaitable[TestClient]], None]
):
    clients = []

    async def build_client(
        __param: web.Application,
        *,
        server_kwargs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Awaitable[TestClient]:
        server_kwargs = server_kwargs or {}
        server = TestServer(__param, **server_kwargs)
        client = TestClient(server, **kwargs)

        await client.start_server()
        clients.append(client)
        return client

    yield build_client

    while clients:
        await clients.pop().close()


@pytest.fixture(scope="module")
async def app(dsn: str) -> AsyncGenerator[FastAPI, None]:
    from main import create_app

    app = create_app(enable_monitoring=False)
    app.router.lifespan_context = lifespan
    app.state.engine = get_sqlalchemy_engine(dsn, debug=False)
    await create_sqlalchemy_tables(app.state.engine)

    yield app

    await drop_sqlalchemy_tables(app.state.engine)
    await app.state.engine.dispose()
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def context() -> dict:
    return dict()


@pytest.fixture(scope="module")
def app_client_factory(
    aiohttp_client: Callable[[web.Application], Awaitable[TestClient]],
    app: FastAPI,
) -> Callable[[web.Application], AsyncGenerator[AppClient, None]]:
    """FastAPI test client with test aiohttp session"""

    @asynccontextmanager
    async def build_client(
        web_app: web.Application,
    ) -> AsyncGenerator[AsyncClient, None]:
        http_client = await aiohttp_client(web_app)

        def get_http_client_override() -> AiohttpClient:
            return AiohttpClient(http_client, http_client.session)

        app.state.http_session = http_client.session
        app.dependency_overrides[get_http_client] = get_http_client_override

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test_api"
        ) as aclient:
            yield AppClient(client=aclient, engine=app.state.engine)

    return build_client


@pytest.fixture(scope="module")
def client(app_client: AppClient) -> AsyncClient:
    return app_client.client


@pytest.fixture(scope="module")
async def empty_client(
    app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    """FastAPI test client without aiohttp session"""
    app.state.http_session = None
    app.dependency_overrides[get_bas_worker] = lambda: None

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test_api"
    ) as aclient:
        yield aclient


type CaptchaClientFactory = Callable[
    [type[BaseRecaptchaClient], AiohttpClientEndpoint],
    Awaitable[BaseRecaptchaClient],
]


@pytest.fixture
def captcha_client_factory(
    aiohttp_client: Callable[[web.Application], Awaitable[TestClient]],
) -> CaptchaClientFactory:
    async def build_client(
        captcha_client: type[BaseRecaptchaClient],
        *endpoints: AiohttpClientEndpoint,
    ) -> Awaitable[BaseRecaptchaClient]:
        web_app = App()
        for endpoint in endpoints:
            web_app.app.router.add_route(
                endpoint.method.upper(),
                endpoint.router,
                getattr(web_app, endpoint.handler),
            )
        _aiohttp_client = await aiohttp_client(web_app.app)
        http_client = AiohttpClient(
            _aiohttp_client, _aiohttp_client.session
        )
        return captcha_client(http_client=http_client)

    return build_client


type BasAuthFactory = Callable[
    [AiohttpClientEndpoint],
    Awaitable[BasAuthClient],
]


@pytest.fixture
def bas_auth_factory(
    aiohttp_client: Callable[[web.Application], Awaitable[TestClient]],
    mocker: MockerFixture,
) -> BasAuthFactory:
    mocker.patch.object(
        BasAuthClient, "_get_recaptcha_site_key", return_value="test_site_key"
    )
    mocker.patch.object(
        BasAuthClient, "_solve_captcha", return_value="test_token"
    )

    async def build_client(
        *endpoints: AiohttpClientEndpoint,
    ) -> Awaitable[BasAuthClient]:
        web_app = App()
        for endpoint in endpoints:
            web_app.app.router.add_route(
                endpoint.method.upper(),
                endpoint.router,
                getattr(web_app, endpoint.handler),
            )
        _aiohttp_client = await aiohttp_client(web_app.app)
        http_client = AiohttpClient(
            _aiohttp_client, _aiohttp_client.session
        )
        return BasAuthClient(
            http_client=http_client,
            captcha_client=None,
            username="42",
            password="42",
        )

    return build_client


@pytest.fixture(scope="module")
def uow(app_client: AppClient) -> IUnitOfWork:
    session_factory = async_sessionmaker(
        app_client.engine, autoflush=False, expire_on_commit=False
    )
    return UnitOfWork(session_factory)
