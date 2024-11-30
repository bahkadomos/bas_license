class BasError(Exception):
    pass


class BasAuthError(BasError):
    def __init__(self) -> None:
        super().__init__("BAS authorization failed")


class BasParseSiteKeyError(BasError):
    def __init__(self) -> None:
        super().__init__("Failed to parse recaptcha site-key")


class BasPremiumExpiredError(BasError):
    def __init__(self) -> None:
        super().__init__("BAS Premium license has expired")


class BasCookieError(BasError):
    def __init__(self) -> None:
        super().__init__("Failed to parse BAS cookie")


class BasRecaptchaSolvedWrongError(BasError):
    def __init__(self) -> None:
        super().__init__("Recaptcha solved wrong")
