from collections.abc import AsyncGenerator, Callable

import pytest
from httpx import AsyncClient

from .conftest import AppClient
from .helpers import (
    App,
    get_success_response_data,
    license_create_task,
)

USER_ACTIVE = "active"
USER_EXPIRED = "expired"
SCRIPT_NAME = "test_script"
usernames = [USER_ACTIVE, USER_EXPIRED]

pytestmark = pytest.mark.asyncio(loop_scope="module")


@pytest.fixture(scope="module")
async def app_client(
    app_client_factory: Callable[[App], AsyncGenerator[AppClient, None]],
) -> AsyncGenerator[AppClient, None]:
    web_app = App()
    web_app.app.router.add_post(
        "/bas/users/page",
        web_app.user_license_succeed_handler,
    )
    web_app.app.router.add_post(
        "/login",
        web_app.bas_success_authorized_handler,
    )
    async with app_client_factory(web_app.app) as client:
        yield client


@pytest.mark.dependency(scope="module")
async def test_license_pending_create_task(
    client: AsyncGenerator[AsyncClient, None],
    context: dict,
):
    task_id = await license_create_task(
        client=client, username="42", script_name="42"
    )
    context["task_id"] = task_id


@pytest.mark.dependency(
    depends=["test_license_pending_create_task"],
    scope="module",
)
async def test_license_pending_get_result(
    client: AsyncClient,
    context: dict,
):
    task_id = context["task_id"]
    data = dict(task_id=task_id)
    response = await client.post("/v1/license/result/", json=data)
    assert response.status_code == 200
    data = get_success_response_data(response)
    assert data.get("status") == "pending"
    assert data.get("is_expired") is None
    assert data.get("expires_in") is None
