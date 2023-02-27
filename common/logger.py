import logging
import logging.config
from functools import wraps
from logging import Logger
from typing import Callable, ParamSpec, TypeVar

logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "std_format": {
            "format": "{asctime} - {levelname:<8} - {name} - {threadName:<8} - {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": logging.DEBUG,
            "formatter": "std_format",
        },
        # "file": {
        #     "class": "logging.FileHandler",
        #     "level": "DEBUG",
        #     "filename": "logs/debug.log",
        #     "formatter": "std_format",
        # },
    },
    "loggers": {
        # Main Logger
        "MLGGR": {
            "level": logging.DEBUG,
            "handlers": [
                "console",
                # "file",
            ]
            # 'propagate': False
        }
    },
    # 'filters': {},
    # 'root': {}   # '': {}
    # 'incremental': True
}


class MyLogger:
    """Create a logger with custom settings."""

    def __init__(self) -> None:
        logging.config.dictConfig(logger_config)

    def get_logger(self, name: str | None = None) -> Logger:
        """Get a logger object."""
        return logging.getLogger(name)


def get_main_logger() -> Logger:
    """Get the main custom logger."""
    return MyLogger().get_logger("MLGGR")


P = ParamSpec("P")
R = TypeVar("R")


def log(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator for functions that need to be logged."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger: Logger = get_main_logger()

        logger.debug(f"Enter: {func.__qualname__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exit: {func.__qualname__}")
            return result
        except Exception as exc:
            logger.exception(f"Exception raised in {func.__qualname__} - {type(exc)} - {str(exc)}")
            raise exc

    return wrapper
