from collections.abc import AsyncGenerator, Callable

import pytest
from httpx import AsyncClient

from .conftest import AppClient
from .helpers import (
    App,
    get_success_response_data,
    license_create_task,
)

pytestmark = pytest.mark.asyncio(loop_scope="module")


@pytest.fixture(scope="module")
async def app_client(
    app_client_factory: Callable[[App], AsyncGenerator[AppClient, None]],
) -> AsyncGenerator[AppClient, None]:
    web_app = App()
    web_app.app.router.add_post(
        "/bas/users/page",
        web_app.user_license_not_found_handler,
    )
    async with app_client_factory(web_app.app) as client:
        yield client


@pytest.mark.dependency(scope="module")
async def test_license_create_task(
    client: AsyncClient,
    context: dict,
):
    task_id = await license_create_task(
        client=client,
        username="42",
        script_name="42",
    )
    context["task_id"] = task_id


@pytest.mark.dependency(
    depends=["test_license_create_task"],
    scope="module",
)
async def test_license_get_result(
    client: AsyncClient,
    context: dict,
):
    task_id = context.get("task_id")
    data = dict(task_id=task_id)
    response = await client.post("/v1/license/result/", json=data)
    assert response.status_code == 200
    data = get_success_response_data(response)
    assert data.get("status") == "creds_not_found"
    assert data.get("is_expired") is None
    assert data.get("expires_in") is None
