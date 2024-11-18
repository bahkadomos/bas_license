class RecaptchaError(Exception):
    pass


class RecaptchaTimeoutError(RecaptchaError):
    def __init__(self, *, attempts: int) -> None:
        super().__init__(f"Failed to solve captcha for {attempts} attempts")


class RecaptchaUnsolved(RecaptchaError):
    def __init__(self) -> None:
        super().__init__("Captcha unsolvable")
