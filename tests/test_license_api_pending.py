from collections.abc import AsyncGenerator
import pytest
from httpx import AsyncClient

from .helpers import get_success_response_data, license_create_task

pytestmark = pytest.mark.asyncio(loop_scope="module")


@pytest.mark.dependency(scope="module")
async def test_license_create_task(
    empty_client: AsyncGenerator[AsyncClient, None],
    context: dict,
):
    task_id = await license_create_task(
        client=empty_client, username="42", script_name="42"
    )
    context["task_id"] = task_id


@pytest.mark.dependency(
    depends=["test_license_create_task"],
    scope="module",
)
async def test_license_get_result(
    empty_client: AsyncClient,
    context: dict,
):
    task_id = context["task_id"]
    data = dict(task_id=task_id)
    response = await empty_client.post("/v1/license/result/", json=data)
    assert response.status_code == 200
    data = get_success_response_data(response)
    assert data.get("status") == "pending"
    assert data.get("is_expired") is None
    assert data.get("expires_in") is None
