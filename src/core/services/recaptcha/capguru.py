import asyncio
from logging import Logger
from typing import Any

from core.config import settings
from core.enums import CaptchaService
from core.utils import HTTPError, IHTTPClient

from .base import BaseRecaptchaClient
from .exceptions import RecaptchaTimeoutError, RecaptchaUnsolved


class CapguruRecaptchaClient(
    BaseRecaptchaClient, service=CaptchaService.capmonster
):
    KEY = settings.capguru_key
    BASE_URL = "http://api.cap.guru{}"
    CAPTCHA_NOT_READY = "CAPCHA_NOT_READY"
    CAPTCHA_UNSOLVABLE = "ERROR_CAPTCHA_UNSOLVABLE"

    def __init__(self, *, http_client: IHTTPClient, logger: Logger) -> None:
        super().__init__(http_client=http_client, logger=logger)
        self._body = {"key": self.KEY, "json": 1}

    async def _create_task_impl(self, site_key: str, page_url: str) -> str:
        json_body = {
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": page_url,
            **self._body,
        }
        response = await self._client.post(
            self.BASE_URL.format("/in.php"), json=json_body
        )
        response_json = response.json_
        assert response_json, f"[cap.guru] {response_json}"
        task_id = response_json.get("request")
        assert task_id and response_json.get("status"), f"[cap.guru] {task_id}"
        return task_id

    async def _get_token_impl(self, task_id: Any) -> str:
        json_body = {"action": "get", "id": task_id, **self._body}
        for _ in range(self._attempts):
            try:
                response = await self._client.post(
                    self.BASE_URL.format("/res.php"), json=json_body
                )
            except HTTPError:
                continue
            response_json = response.json_
            assert response_json, f"[cap.guru] {response_json}"
            token = response_json.get("request")
            if token == self.CAPTCHA_NOT_READY:
                await asyncio.sleep(self._delay)
                continue
            if token == self.CAPTCHA_UNSOLVABLE:
                raise RecaptchaUnsolved()
            assert isinstance(token, str), f"[cap.guru] Token is {type(token)}"
            assert response_json.get("status"), f"[cap.guru] {token}"
            return token
        raise RecaptchaTimeoutError(attempts=self._attempts)
