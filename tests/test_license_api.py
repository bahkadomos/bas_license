import uuid
from collections.abc import AsyncGenerator, Callable
from datetime import datetime

import pytest
from httpx import AsyncClient

from core.services.uow import IUnitOfWork

from .conftest import AppClient
from .helpers import (
    App,
    get_error_response_data,
    get_success_response_data,
    license_create_task,
)

USER_ACTIVE = "active"
USER_EXPIRED = "expired"
SCRIPT_NAME = "test_script"
usernames = [USER_ACTIVE, USER_EXPIRED]

pytestmark = [
    pytest.mark.asyncio(loop_scope="module"),
    pytest.mark.use_set_session,
]


@pytest.fixture(scope="module")
async def app_client(
    app_client_factory: Callable[[App], AsyncGenerator[AppClient, None]],
) -> AsyncGenerator[AppClient, None]:
    web_app = App()
    web_app.app.router.add_post(
        "/bas/users/page",
        web_app.user_license_succeed_handler,
    )
    async with app_client_factory(web_app.app) as client:
        yield client


@pytest.mark.dependency(scope="module")
@pytest.mark.parametrize("username", usernames)
async def test_license_create_task(
    client: AsyncClient,
    context: dict,
    username: str,
):
    task_id = await license_create_task(
        client=client,
        username=username,
        script_name=SCRIPT_NAME,
    )
    context[f"{username}_task_id"] = task_id


@pytest.mark.dependency(
    depends=[
        f"test_license_create_task[{USER_ACTIVE}]",
        f"test_license_create_task[{USER_EXPIRED}]",
    ],
    scope="module",
)
@pytest.mark.parametrize("username", usernames)
async def test_task_id_in_db(uow: IUnitOfWork, context: dict, username: str):
    expected_task_id = context[f"{username}_task_id"]
    async with uow:
        task = await uow.license_tasks.read_one(expected_task_id)
        await uow.commit()

    assert isinstance(task.id, uuid.UUID) and str(task.id) == expected_task_id
    context[f"{username}_task_model"] = task


@pytest.mark.dependency(
    depends=[
        f"test_license_create_task[{USER_ACTIVE}]",
        f"test_license_create_task[{USER_EXPIRED}]",
    ],
    scope="module",
)
@pytest.mark.parametrize("username", usernames)
async def test_user_in_db(uow: IUnitOfWork, username: str):
    async with uow:
        res = await uow.users.read(filter_by=dict(username=username))
        await uow.commit()
    assert res.scalar_one_or_none()


@pytest.mark.dependency(
    depends=[f"test_license_create_task[{USER_EXPIRED}]"],
    scope="module",
)
async def test_script_in_db(uow: IUnitOfWork):
    async with uow:
        res = await uow.scripts.read(filter_by=dict(script_name=SCRIPT_NAME))
        await uow.commit()
    assert res.scalar_one_or_none()


@pytest.mark.dependency(
    depends=[
        f"test_license_create_task[{USER_ACTIVE}]",
        f"test_license_create_task[{USER_EXPIRED}]",
    ],
    scope="module",
)
@pytest.mark.parametrize("username", usernames)
async def test_license_get_result(
    client: AsyncClient,
    context: dict,
    username: str,
):
    task_id = context.get(f"{username}_task_id")
    data = dict(task_id=task_id)
    response = await client.post("/v1/license/result/", json=data)
    assert response.status_code == 200
    data = get_success_response_data(response)
    context[f"{username}_result_data"] = data


@pytest.mark.dependency(
    depends=[
        f"test_license_get_result[{USER_ACTIVE}]",
        f"test_license_get_result[{USER_EXPIRED}]",
    ],
    scope="module",
)
@pytest.mark.parametrize("username", usernames)
async def test_result_status_ok(context: dict, username: str):
    data = context[f"{username}_result_data"]
    assert data.get("status") == "ok"


@pytest.mark.dependency(
    depends=[
        f"test_license_get_result[{USER_ACTIVE}]",
        f"test_license_get_result[{USER_EXPIRED}]",
    ],
    scope="module",
)
@pytest.mark.parametrize("username", usernames)
async def test_received_credentials(context: dict, username: str):
    data = context[f"{username}_result_data"]
    credentials = data.get("credentials")
    assert isinstance(
        credentials, dict
    ), f"Credentials must be a dict, not {type(credentials)}"
    assert len(credentials), "Empty credentials"
    context[f"{username}_credentials"] = credentials


@pytest.mark.dependency(
    depends=[
        f"test_received_credentials[{USER_ACTIVE}]",
        f"test_received_credentials[{USER_EXPIRED}]",
    ],
    scope="module",
)
@pytest.mark.parametrize(
    ("username", "expected_expired"),
    [(USER_ACTIVE, False), (USER_EXPIRED, True)],
)
async def test_license_is_expired(
    context: dict, username: str, expected_expired: bool
):
    credentials = context[f"{username}_credentials"]
    assert credentials.get("is_expired") is expected_expired


@pytest.mark.dependency(
    depends=[
        f"test_received_credentials[{USER_ACTIVE}]",
        f"test_received_credentials[{USER_EXPIRED}]",
    ],
    scope="module",
)
@pytest.mark.parametrize(
    ("username", "expected_expired"),
    [(USER_ACTIVE, False), (USER_EXPIRED, True)],
)
async def test_license_expires_in(
    context: dict, username: str, expected_expired: bool
):
    credentials = context[f"{username}_credentials"]
    expires_in = credentials.get("expires_in")
    assert isinstance(
        expires_in, str
    ), f"Key 'credentials.expires_in' is {type(expires_in)}, expected 'str'"

    try:
        date = datetime.fromisoformat(expires_in)
    except ValueError as e:
        raise AssertionError(
            "Date by key 'credentials.expires_in' is invalid"
        ) from e

    is_expired = date < datetime.now()
    assert is_expired is expected_expired


async def test_task_id_not_found(client: AsyncClient):
    data = dict(task_id=str(uuid.uuid4()))
    response = await client.post("/v1/license/result/", json=data)
    assert response.status_code == 404
    data = get_error_response_data(response)
    assert data.get("location") == "body"
    assert data.get("field") == "task_id"
    assert data.get("description") == "Task id not found"
