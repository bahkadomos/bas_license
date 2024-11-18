import asyncio
from typing import Any

from core.config import CaptchaService, settings
from core.utils import HTTPError, IHTTPClient

from .base import BaseRecaptchaClient
from .exceptions import RecaptchaTimeoutError, RecaptchaUnsolved


class CapmonsterRecaptchaClient(
    BaseRecaptchaClient, service=CaptchaService.capmonster
):
    KEY = settings.capmonster_key
    BASE_URL = "https://api.capmonster.cloud{}"
    CAPTCHA_NOT_READY = "processing"
    CAPTCHA_SOLVED = "ready"
    CAPTCHA_UNSOLVABLE = "ERROR_CAPTCHA_UNSOLVABLE"

    def __init__(self, *, http_client: IHTTPClient) -> None:
        super().__init__(http_client=http_client)
        self._body = {"clientKey": self.KEY}

    async def _create_task_impl(self, site_key: str, page_url: str) -> int:
        json_body = {
            **self._body,
            "task": {
                "type": "RecaptchaV2TaskProxyless",
                "websiteURL": page_url,
                "websiteKey": site_key,
            },
        }
        response = await self._client.post(
            self.BASE_URL.format("/createTask"), json=json_body
        )
        response_json = response.json_
        assert response_json, f"[capmonster.cloud] {response_json}"
        assert (
            response_json.get("errorId") == 0
        ), f"[capmonster.cloud] {self._get_error_string(response_json)}"
        task_id = response_json.get("taskId")
        assert isinstance(
            task_id, int
        ), f"[capmonster.cloud] task_id is {type(task_id)}"
        return task_id

    async def _get_token_impl(self, task_id: Any) -> str:
        json_body = {**self._body, "taskId": task_id}
        for _ in range(self._attempts):
            try:
                response = await self._client.post(
                    self.BASE_URL.format("/getTaskResult"), json=json_body
                )
            except HTTPError:
                continue
            response_json = response.json_
            assert response_json, f"[capmonster.cloud] {response_json}"
            status = response_json.get("status")
            error_code = response_json.get("errorCode")
            if status == self.CAPTCHA_NOT_READY:
                await asyncio.sleep(self._delay)
                continue
            if error_code == self.CAPTCHA_UNSOLVABLE:
                raise RecaptchaUnsolved()
            if status == self.CAPTCHA_SOLVED:
                return response_json["solution"]["gRecaptchaResponse"]
            assert (
                response_json.get("errorId") == 0
            ), f"[capmonster.cloud] {self._get_error_string(response_json)}"
        raise RecaptchaTimeoutError(attempts=self._attempts)

    def _get_error_string(self, response_json: dict[str, Any]) -> str:
        return (
            response_json.get("errorDescription")
            or response_json.get("errorCode")
            or "UNKNOWN_ERROR"
        )
