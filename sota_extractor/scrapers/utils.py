import requests
from datetime import datetime
from typing import Optional, Union

import pytz
from bs4 import BeautifulSoup


def get_soup(url):
    """Get a BeautifulSoup object back from the a URL.

    Args:
        url: URL to scrape.
    """

    r = requests.get(url)

    if r.status_code == 404:
        return None

    data = r.text
    return BeautifulSoup(data, "lxml")


def date_from_timestamp(
    timestamp: Optional[Union[int, str]], tz: str = "UTC"
) -> Optional[datetime]:
    """Get date from int or string timestamp.

    Args:
        timestamp: Timestamp to parse.
        tz: Optional timezone to use.
    """
    if timestamp is None:
        return None

    if isinstance(timestamp, str):
        try:
            timestamp = int(timestamp)
        except ValueError:
            return None

    try:
        return datetime.fromtimestamp(timestamp, pytz.timezone(tz)).replace(
            tzinfo=pytz.utc
        )
    except (TypeError, ValueError):
        return None


def sround(
    x: Union[int, float, str], ndigits: int = 3, default: float = 0.0
) -> str:
    """Round the number and return as a string.

    Args:
        x (int|float|str): Number to format.
        ndigits (int): Number of digits to enforce.
        default (float): Default value if rounding fails.

    Returns:
        str: Rounded string representation.
    """
    try:
        x = round(float(x), ndigits=ndigits)
    except ValueError:
        x = default

    return "{{:.{}f}}".format(ndigits).format(x)
