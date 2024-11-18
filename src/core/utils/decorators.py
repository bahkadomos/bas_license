from typing import Any
from collections.abc import Awaitable, Callable

type _Func[**P, R] = Callable[P, Awaitable[R]]


def exc_wrapper[**P, R](
    exc_in: type[Exception],
    exc_out: type[Exception],
    *exc_args: Any,
    **exc_kwargs: Any,
) -> Callable[[_Func[P, R]], _Func[P, R]]:
    def decorator(func: _Func[P, R]) -> _Func[P, R]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await func(*args, **kwargs)
            except exc_in as e:
                raise exc_out(*exc_args, **exc_kwargs) from e

        return wrapper

    return decorator
