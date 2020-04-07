import click
import logging
import functools
from requests import Response

from sota_extractor.consts import DEBUG


logger = logging.getLogger(__name__)


class SotaError(Exception):
    def __init__(self, message):
        self.message = message

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return f"{self.name}(message={self.message})"

    __repr__ = __str__


class DataError(SotaError):
    pass


class ArgumentError(SotaError):
    pass


class HttpClientError(SotaError):
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response: Response = response
        self.status_code = (
            response.status_code if response is not None else 500
        )

    def __str__(self):
        return (
            f"{self.name}(message={self.message}, "
            f"status_code={self.status_code})"
        )

    __repr__ = __str__


class UnsupportedFormat(SotaError):
    def __init__(self, fmt):
        super().__init__(f"Unsupported serialization format: {fmt.value}")
        self.fmt = fmt


def catch_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except SotaError as e:
            click.secho(str(e), fg="red")
        except Exception as e:

            if DEBUG:
                logger.exception("Unknown error: %s", e)
            else:
                click.secho(f"Unknown error: {e}", fg="red")

    return wrapper
