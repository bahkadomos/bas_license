from collections.abc import Awaitable

import pytest
from pytest_mock import MockerFixture

from core.services.bas import (
    BasAuthClient,
    BasAuthError,
    BasCookieError,
    BasPremiumExpiredError,
    BasRecaptchaSolvedWrongError,
)

from .conftest import AiohttpClientEndpoint

pytestmark = pytest.mark.asyncio(loop_scope="module")


@pytest.fixture
async def auth_success_client(
    bas_auth_factory: Awaitable[BasAuthClient],
) -> BasAuthClient:
    client = await bas_auth_factory(
        AiohttpClientEndpoint(
            router="/login",
            handler="any_text_response_handler",
            method="GET",
        ),
        AiohttpClientEndpoint(
            router="/login",
            handler="bas_success_redirect_handler",
            method="POST",
        ),
        AiohttpClientEndpoint(
            router="/personal/license/BASPremium",
            handler="bas_success_authorized_handler",
            method="GET",
        ),
    )
    return client


@pytest.fixture
async def auth_empty_cookie_client(
    bas_auth_factory: Awaitable[BasAuthClient],
) -> BasAuthClient:
    client = await bas_auth_factory(
        AiohttpClientEndpoint(
            router="/login",
            handler="any_text_response_handler",
            method="GET",
        ),
        AiohttpClientEndpoint(
            router="/login",
            handler="bas_success_redirect_handler",
            method="POST",
        ),
        AiohttpClientEndpoint(
            router="/personal/license/BASPremium",
            handler="bas_authorized_empty_cookie_handler",
            method="GET",
        ),
    )
    return client


@pytest.fixture
async def auth_not_redirect(
    bas_auth_factory: Awaitable[BasAuthClient],
) -> BasAuthClient:
    client = await bas_auth_factory(
        AiohttpClientEndpoint(
            router="/login",
            handler="any_text_response_handler",
            method="GET",
        ),
        AiohttpClientEndpoint(
            router="/login",
            handler="any_text_response_handler",
            method="POST",
        ),
    )
    return client


async def test_auth_succeed(auth_success_client: BasAuthClient):
    await auth_success_client.get_session_cookie()


async def test_recaptcha_solved_wrong(
    auth_success_client: BasAuthClient, mocker: MockerFixture
):
    mocker.patch.object(
        BasAuthClient,
        "_get_auth_error",
        return_value="Please check recaptcha",
    )
    with pytest.raises(BasRecaptchaSolvedWrongError):
        await auth_success_client.get_session_cookie()


async def test_unknown_error(
    auth_success_client: BasAuthClient, mocker: MockerFixture
):
    mocker.patch.object(
        BasAuthClient,
        "_get_auth_error",
        return_value="42",
    )
    with pytest.raises(BasAuthError):
        await auth_success_client.get_session_cookie()


async def test_bas_premium_expired(auth_not_redirect: BasAuthClient):
    with pytest.raises(BasPremiumExpiredError):
        await auth_not_redirect.get_session_cookie()


async def test_empty_cookie(auth_empty_cookie_client: BasAuthClient):
    with pytest.raises(BasCookieError):
        await auth_empty_cookie_client.get_session_cookie()
