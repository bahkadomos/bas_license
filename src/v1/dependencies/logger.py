from logging import Logger
from typing import Annotated

from fastapi import Depends, Request


def get_logger(request: Request) -> Logger:
    return request.app.state.logger


LoggerDependency = Annotated[Logger, Depends(get_logger)]
