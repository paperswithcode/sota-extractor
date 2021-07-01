import logging
from datetime import datetime

from sota_extractor.scrapers.utils import get_soup
from sota_extractor.taskdb.v01 import (
    Link,
    Task,
    Dataset,
    SotaRow,
    TaskDB,
)


logger = logging.getLogger(__name__)


DATA = [
    {
        "url": "https://ogb.stanford.edu/docs/leader_nodeprop/",
        "datasets": [
            "ogbn-products",
            "ogbn-proteins",
            "ogbn-arxiv",
            "ogbn-papers100M",
            "ogbn-mag",
        ],
        "task": "Node Property Prediction",
    },
    {
        "url": "https://ogb.stanford.edu/docs/leader_linkprop/",
        "datasets": [
            "ogbl-ppa",
            "ogbl-collab",
            "ogbl-ddi",
            "ogbl-citation2",
            "ogbl-wikikg2",
            "ogbl-biokg",
        ],
        "task": "Link Property Prediction",
    },
    {
        "url": "https://ogb.stanford.edu/docs/leader_graphprop/",
        "datasets": ["ogbg-molhiv", "ogbg-molpcba", "ogbg-ppa", "ogbg-code2"],
        "task": "Graph Property Prediction",
    },
]


def get_sota_rows(url: str, dataset: Dataset):
    try:
        soup = get_soup(url)

        h3 = soup.find(id=f"leaderboard-for-{dataset.name}".lower())
        table = h3.find_next_sibling("table")

        headers = table.find_all("th")
        metric_1 = headers[2].text
        metric_2 = headers[3].text
        metric_3 = "Number of params"

        dataset.sota.metrics = [metric_1, metric_2, metric_3]
        for tr in table.select("tbody > tr"):
            tds = tr.find_all("td")

            try:
                paper_url = tds[5].find("a", text="Paper").attrs["href"]
            except (AttributeError, KeyError):
                paper_url = ""

            try:
                paper_date = datetime.strptime(tds[8].text, "%b %d, %Y")
            except ValueError:
                paper_date = None

            try:
                link = Link(url=tds[5].find("a", text="Code").attrs["href"])
                code_links = [link]
            except (AttributeError, KeyError):
                code_links = []

            dataset.sota.rows.append(
                SotaRow(
                    model_name=tds[1].text,
                    paper_url=paper_url,
                    paper_date=paper_date,
                    code_links=code_links,
                    metrics={
                        metric_1: tds[2].text,
                        metric_2: tds[3].text,
                        metric_3: tds[6].text.replace(",", ""),
                    },
                )
            )
    except Exception as e:
        logger.exception(
            "Failed to get dataset: %s. Error: %s", dataset.name, e
        )


def ogb() -> TaskDB:
    """Extract OGB SOTA tables."""
    tdb = TaskDB()

    for item in DATA:
        url = item["url"]

        task = Task(
            name=item["task"],
            source_link=Link(title=f"{item['task']} LeaderBoard", url=url),
        )
        tdb.add_task(task)
        for dataset_name in item["datasets"]:
            dataset = Dataset(name=dataset_name)
            task.datasets.append(dataset)
            get_sota_rows(url, dataset)
    return tdb
