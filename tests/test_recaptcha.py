from typing import Any
import pytest

from core.services.recaptcha import (
    BaseRecaptchaClient,
    CapguruRecaptchaClient,
    CapmonsterRecaptchaClient,
    RecaptchaError,
    RecaptchaUnsolved,
)

from .conftest import AiohttpClientEndpoint, CaptchaClientFactory

pytestmark = pytest.mark.asyncio(loop_scope="module")

success_create_task_handlers = [
    (
        CapguruRecaptchaClient,
        AiohttpClientEndpoint(
            router="/in.php",
            handler="capguru_create_task_handler",
            method="POST",
        ),
        str,
    ),
    (
        CapmonsterRecaptchaClient,
        AiohttpClientEndpoint(
            router="/createTask",
            handler="capmonster_create_task_handler",
            method="POST",
        ),
        int,
    ),
]
error_create_task_handlers = [
    (
        CapguruRecaptchaClient,
        AiohttpClientEndpoint(
            router="/in.php",
            handler="capguru_create_task_error_handler",
            method="POST",
        ),
    ),
    (
        CapmonsterRecaptchaClient,
        AiohttpClientEndpoint(
            router="/createTask",
            handler="capmonster_create_task_error_handler",
            method="POST",
        ),
    ),
]

ready_get_result_handlers = [
    (
        CapguruRecaptchaClient,
        AiohttpClientEndpoint(
            router="/res.php",
            handler="capguru_result_ready_handler",
            method="POST",
        ),
        "42",
        str,
    ),
    (
        CapmonsterRecaptchaClient,
        AiohttpClientEndpoint(
            router="/getTaskResult",
            handler="capmonster_result_ready_handler",
            method="POST",
        ),
        42,
        str,
    ),
]
unsolvable_get_result_handlers = [
    (
        CapguruRecaptchaClient,
        AiohttpClientEndpoint(
            router="/res.php",
            handler="capguru_result_unsolvable_handler",
            method="POST",
        ),
        "42",
    ),
    (
        CapmonsterRecaptchaClient,
        AiohttpClientEndpoint(
            router="/getTaskResult",
            handler="capmonster_result_unsolvable_handler",
            method="POST",
        ),
        42,
    ),
]
unhandled_error_get_result_handlers = [
    (
        CapguruRecaptchaClient,
        AiohttpClientEndpoint(
            router="/res.php",
            handler="capguru_result_unhandled_error_handler",
            method="POST",
        ),
        "42",
    ),
    (
        CapmonsterRecaptchaClient,
        AiohttpClientEndpoint(
            router="/getTaskResult",
            handler="capmonster_result_unhandled_error_handler",
            method="POST",
        ),
        42,
    ),
]


@pytest.mark.parametrize(
    ("captcha_client", "endpoint", "return_type"),
    success_create_task_handlers,
)
async def test_create_task_succeed(
    captcha_client_factory: CaptchaClientFactory,
    captcha_client: type[BaseRecaptchaClient],
    endpoint: AiohttpClientEndpoint,
    return_type: Any,
):
    client = await captcha_client_factory(captcha_client, endpoint)
    task_id = await client.create_task("test_site_key", "test_page_url")
    assert isinstance(task_id, return_type)


@pytest.mark.parametrize(
    ("captcha_client", "endpoint"),
    error_create_task_handlers,
)
async def test_create_task_error(
    captcha_client_factory: CaptchaClientFactory,
    captcha_client: type[BaseRecaptchaClient],
    endpoint: AiohttpClientEndpoint,
):
    client = await captcha_client_factory(captcha_client, endpoint)
    with pytest.raises(RecaptchaError):
        await client.create_task("test_site_key", "test_page_url")


@pytest.mark.parametrize(
    ("captcha_client", "endpoint", "task_id", "return_type"),
    ready_get_result_handlers,
)
async def test_result_ready(
    captcha_client_factory: CaptchaClientFactory,
    captcha_client: type[BaseRecaptchaClient],
    endpoint: AiohttpClientEndpoint,
    task_id: Any,
    return_type: Any,
):
    client = await captcha_client_factory(captcha_client, endpoint)
    token = await client.get_token(task_id)
    assert isinstance(token, return_type)


@pytest.mark.parametrize(
    ("captcha_client", "endpoint", "task_id"),
    unsolvable_get_result_handlers,
)
async def test_result_unsolvable(
    captcha_client_factory: CaptchaClientFactory,
    captcha_client: type[BaseRecaptchaClient],
    endpoint: AiohttpClientEndpoint,
    task_id: Any,
):
    client = await captcha_client_factory(captcha_client, endpoint)
    with pytest.raises(RecaptchaUnsolved):
        await client.get_token(task_id)


@pytest.mark.parametrize(
    ("captcha_client", "endpoint", "task_id"),
    unhandled_error_get_result_handlers,
)
async def test_result_unhandled_error(
    captcha_client_factory: CaptchaClientFactory,
    captcha_client: type[BaseRecaptchaClient],
    endpoint: AiohttpClientEndpoint,
    task_id: Any,
):
    client = await captcha_client_factory(captcha_client, endpoint)
    with pytest.raises(RecaptchaError):
        await client.get_token(task_id)
