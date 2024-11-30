from http.cookies import SimpleCookie


class CookiesManager:
    @staticmethod
    def dump(cookies: SimpleCookie, name: str) -> str | None:
        val = cookies.get(name)
        if val:
            return val.OutputString()

    @staticmethod
    def load(cookies: str, key: str) -> dict[str, str] | None:
        cookie = SimpleCookie(cookies).get(key)
        if cookie:
            return {cookie.key: cookie.value}
