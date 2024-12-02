import asyncio
from collections.abc import AsyncGenerator, Callable

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from core.services.workers import BasWorker

from .conftest import AppClient
from .helpers import App, license_create_task

pytestmark = pytest.mark.asyncio(loop_scope="module")


@pytest.fixture(scope="module")
async def app_client(
    app_client_factory: Callable[[App], AsyncGenerator[AppClient, None]],
) -> AsyncGenerator[AppClient, None]:
    web_app = App()
    web_app.app.router.add_post(
        "/bas/users/page",
        web_app.user_license_handler,
    )
    web_app.app.router.add_get(
        "/login",
        web_app.any_text_response_handler,
    )
    web_app.app.router.add_post(
        "/login",
        web_app.bas_success_redirect_handler,
    )
    web_app.app.router.add_get(
        "/personal/license/BASPremium",
        web_app.bas_success_authorized_handler,
    )
    web_app.app.router.add_post(
        "/in.php",
        web_app.capguru_create_task_handler,
    )
    web_app.app.router.add_post(
        "/createTask",
        web_app.capmonster_create_task_handler,
    )
    web_app.app.router.add_post(
        "/res.php",
        web_app.capguru_result_ready_handler,
    )
    web_app.app.router.add_post(
        "/getTaskResult",
        web_app.capmonster_result_ready_handler,
    )
    async with app_client_factory(web_app.app) as client:
        yield client


async def test_worker_lock_without_session(
    client: AsyncClient,
    mocker: MockerFixture,
):
    spy_update_session = mocker.spy(BasWorker, "_update_session")

    tasks = []
    for i in range(5):
        task = license_create_task(
            client=client,
            username=f"test_user_{i}",
            script_name=f"test_script_{i}",
        )
        tasks.append(task)

    await asyncio.gather(*tasks)
    assert spy_update_session.call_count == 1
