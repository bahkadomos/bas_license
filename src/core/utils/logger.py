import logging
from typing import Any

from loki_logger_handler.loki_logger_handler import (
    LoggerFormatter,
    LokiLoggerHandler,
)

from core.config import settings
from core.enums import LoggerCallerTypes

LOGGER_NAME = "bas_license"


class LokiLoggerFormatter(LoggerFormatter):
    def format(self, record: logging.LogRecord) -> dict[str, Any]:
        if record.__dict__.get("caller") is None:
            record.__dict__["caller"] = LoggerCallerTypes.common.value
        return super().format(record)


def get_loki_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.ERROR)
    handler = LokiLoggerHandler(
        url=settings.loki_url,
        labels={"application": "bas_license"},
        timeout=10,
        default_formatter=LokiLoggerFormatter()
    )
    logger.addHandler(handler)
    return logger


def get_null_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(logging.NullHandler())
    return logger
