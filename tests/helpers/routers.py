import time

from aiohttp import web


class App:
    SESSION = "test_session"

    def __init__(self) -> None:
        self._app = web.Application()

    @property
    def app(self) -> web.Application:
        return self._app

    async def any_text_response_handler(self, _: web.Request) -> web.Response:
        return web.Response(text="Test response", status=200)

    async def user_license_succeed_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "success": "true",
            "data": [
                {
                    "expires": int(time.time()) + 1000,
                    "user": "active",
                    "script": "test_script",
                },
                {
                    "expires": int(time.time()) - 1000,
                    "user": "expired",
                    "script": "test_script",
                },
            ],
        }
        return web.json_response(data, status=200)

    async def user_license_not_found_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {"success": "true", "data": []}
        return web.json_response(data, status=200)

    async def user_license_no_login_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {"success": "false", "message": "no login"}
        return web.json_response(data, status=200)

    async def user_license_handler(self, request: web.Request) -> web.Response:
        if request.cookies.get("session") == self.SESSION:
            return await self.user_license_succeed_handler(request)
        else:
            return await self.user_license_no_login_handler(request)

    async def bas_success_redirect_handler(
        self, _: web.Request
    ) -> web.Response:
        response = web.Response(status=302)
        response.headers["Location"] = "/personal/license/BASPremium"
        return response

    async def bas_success_authorized_handler(
        self, _: web.Request
    ) -> web.Response:
        response = web.Response(status=200)
        response.set_cookie("session", self.SESSION)
        return response

    async def bas_authorized_empty_cookie_handler(
        self, _: web.Request
    ) -> web.Response:
        response = web.Response(status=200)
        return response

    async def capguru_create_task_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "status": 1,
            "request": "42",
        }
        return web.json_response(data, status=200)

    async def capguru_create_task_error_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "status": 0,
            "request": "42",
        }
        return web.json_response(data, status=200)

    async def capguru_result_ready_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "status": 1,
            "request": "recaptcha_token",
        }
        return web.json_response(data, status=200)

    async def capguru_result_unsolvable_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "status": 0,
            "request": "ERROR_CAPTCHA_UNSOLVABLE",
        }
        return web.json_response(data, status=200)

    async def capguru_result_unhandled_error_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "status": 0,
            "request": "Test error",
        }
        return web.json_response(data, status=200)

    async def capmonster_create_task_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "errorId": 0,
            "taskId": 42,
        }
        return web.json_response(data, status=200)

    async def capmonster_create_task_error_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "errorId": 1,
        }
        return web.json_response(data, status=200)

    async def capmonster_result_ready_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "status": "ready",
            "errorId": 0,
            "solution": {
                "gRecaptchaResponse": "recaptcha_token",
            },
        }
        return web.json_response(data, status=200)

    async def capmonster_result_unsolvable_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "errorId": 1,
            "errorCode": "ERROR_CAPTCHA_UNSOLVABLE",
        }
        return web.json_response(data, status=200)

    async def capmonster_result_unhandled_error_handler(
        self, _: web.Request
    ) -> web.Response:
        data = {
            "errorId": 1,
            "errorCode": "Test error code",
            "errorDescription": "Test error description",
        }
        return web.json_response(data, status=200)
