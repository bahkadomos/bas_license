from collections.abc import Sequence
from datetime import datetime
from http.cookies import CookieError

from lxml import etree

from core.enums import LicenseResultStatus
from core.schemas import LicenseDetailsSchema
from core.services.recaptcha import BaseRecaptchaClient
from core.utils import (
    CookiesManager,
    HTTPResponseType,
    IHTTPClient,
    TextHTTPResponse,
)

from .exceptions import (
    BasAuthError,
    BasCookieError,
    BasParseSiteKeyError,
    BasPremiumExpiredError,
    BasRecaptchaSolvedWrongError,
)
from .schemas import LicenseResponseResultSchema


class BaseBasClient:
    SESSION_COOKIE_KEY = "session"

    def __init__(self, http_client: IHTTPClient) -> None:
        self._client = http_client

    def set_session_cookie(self, cookies: str) -> None:
        try:
            cookies_dict = CookiesManager.load(
                cookies, self.SESSION_COOKIE_KEY
            )
        except CookieError as e:
            raise BasCookieError() from e
        if cookies_dict is None:
            raise BasCookieError()
        self._client.set_cookie(cookies_dict)


class BasAuthClient(BaseBasClient):
    BASE_URL = "https://bablosoft.com{}"
    CAPTCHA_SOLVED_WRONG = "Please check recaptcha"

    def __init__(
        self,
        *,
        http_client: IHTTPClient,
        captcha_client: BaseRecaptchaClient,
        username: str,
        password: str,
    ) -> None:
        super().__init__(http_client)
        self._captcha_client = captcha_client
        self._username = username
        self._password = password
        self._parser = etree.HTMLParser()

    @property
    def LOGIN_URL(self) -> str:
        return self.BASE_URL.format("/login")

    @property
    def SUCCESS_URL(self) -> str:
        return self.BASE_URL.format("/personal/license/BASPremium")

    def _get_dom_value(self, html: str, query: str) -> str | None:
        dom = etree.fromstring(html, self._parser)
        data = dom.xpath(query)
        if (
            isinstance(data, Sequence)
            and len(data)
            and isinstance(data[0], str)
        ):
            return data[0]

    def _get_recaptcha_site_key(self, html: str) -> str | None:
        return self._get_dom_value(
            html, '//div[@class="g-recaptcha"]/@data-sitekey'
        )

    def _get_auth_error(self, html: str) -> str | None:
        return self._get_dom_value(html, '//div[@role="alert"]/text()')

    async def _init_login(self) -> TextHTTPResponse:
        return await self._client.get(
            self.LOGIN_URL, response_type=HTTPResponseType.text
        )

    async def _solve_captcha(self, site_key: str) -> str:
        task_id = await self._captcha_client.create_task(
            site_key, self.LOGIN_URL
        )
        token = await self._captcha_client.get_token(task_id)
        return token

    async def _login(self, token: str) -> TextHTTPResponse:
        body = {
            "username": self._username,
            "password": self._password,
            "g-recaptcha-response": token,
        }
        return await self._client.post(
            self.LOGIN_URL, response_type=HTTPResponseType.text, data=body
        )

    async def get_session_cookie(self) -> str | None:
        response = await self._init_login()
        site_key = self._get_recaptcha_site_key(response.data)
        if site_key is None:
            raise BasParseSiteKeyError()

        token = await self._solve_captcha(site_key)
        response = await self._login(token)
        error = self._get_auth_error(response.data)
        if error == self.CAPTCHA_SOLVED_WRONG:
            raise BasRecaptchaSolvedWrongError()
        elif error is not None:
            raise BasAuthError()

        if response.url.human_repr() != self.SUCCESS_URL:
            raise BasPremiumExpiredError()
        cookies = self._client.get_cookie()
        if not cookies.values():
            raise BasCookieError()
        try:
            return CookiesManager.dump(cookies, self.SESSION_COOKIE_KEY)
        except CookieError as e:
            raise BasCookieError() from e


class BasAPIClient(BaseBasClient):
    BASE_URL = "https://bablosoft.com{}"
    API_NOT_AUTHORIZED = "no login"

    @property
    def API_USERS_URL(self) -> str:
        return self.BASE_URL.format("/bas/users/page")

    async def get_user_license(
        self, user: str, script: str
    ) -> LicenseResponseResultSchema:
        json_body = {"page": 0, "user": user, "script": script}
        response = await self._client.post(self.API_USERS_URL, json=json_body)
        match response.json_:
            case {"success": "true", "data": list() as items}:
                licenses = [
                    item
                    for item in items
                    if item.get("user") == user
                    and item.get("script") == script
                ]
                if not licenses:
                    return LicenseResponseResultSchema(
                        status=LicenseResultStatus.creds_not_found
                    )
                details = licenses[0]
                expires = datetime.fromtimestamp(details["expires"])
                is_expired = expires < datetime.now()
                return LicenseResponseResultSchema(
                    status=LicenseResultStatus.ok,
                    credentials=LicenseDetailsSchema(
                        is_expired=is_expired, expires_in=expires
                    ),
                )
            case {"success": "false", "message": self.API_NOT_AUTHORIZED}:
                return LicenseResponseResultSchema(
                    status=LicenseResultStatus.not_authorized
                )
            case _:
                return LicenseResponseResultSchema(
                    status=LicenseResultStatus.error
                )
