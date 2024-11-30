from json import JSONDecodeError
from typing import Any

from fastapi import Response
from httpx import AsyncClient


def get_response_data(
    response: Response, *, expected_error: bool
) -> dict[str, Any]:
    try:
        body = response.json()
    except JSONDecodeError as e:
        raise AssertionError(f"Response is not a valid JSON: {e}") from e

    data = body.get("data")
    assert data, "FIeld 'data' in response is missing"
    assert body.get(
        "server_info"
    ), "Field 'server_info' in response is missing"
    error = body.get("error")
    assert (
        error is expected_error
    ), f"Field 'error' in response must be {expected_error}, not {error}"
    assert response.headers.get(
        "x-signature"
    ), "Header 'X-Signature' is missing"

    return data


def get_success_response_data(response: Response) -> dict[str, Any]:
    return get_response_data(response, expected_error=False)


def get_error_response_data(response: Response) -> dict[str, Any]:
    return get_response_data(response, expected_error=True)


async def license_create_task(
    *,
    client: AsyncClient,
    username: str,
    script_name: str
) -> str:
    data = dict(username=username, script_name=script_name)
    response = await client.post("/v1/license/", json=data)
    assert response.status_code == 201
    data = get_success_response_data(response)
    task_id = data.get("task_id")
    assert isinstance(
        task_id, str
    ), f"Field 'data.task_id' must be UUID, not {type(task_id)}"
    return task_id
