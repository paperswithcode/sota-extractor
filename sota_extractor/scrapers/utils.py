import requests
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
