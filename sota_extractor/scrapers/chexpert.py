import requests

from sota_extractor.errors import HttpClientError
from sota_extractor.scrapers.utils import date_from_timestamp, sround
from sota_extractor.taskdb.v01 import SotaRow, Dataset, Task, Link, TaskDB


URL = "https://stanfordmlgroup.github.io/competitions/chexpert/"
JSON_URL = (
    "https://raw.githubusercontent.com/stanfordmlgroup/"
    "stanfordmlgroup.github.io/master/competitions/chexpert/out.json"
)

TASK_NAME = "Multi-Label Classification"
DATASET_NAME = "CheXpert"


def get_sota_rows(data):
    rows = data["leaderboard"]

    sota_rows = []
    for row in rows:
        # HACK: This hack with the timezone is needed because they don't use
        #       timezones. They just run the gulp html generation script in
        #       localtime which is (I guess) Stanford i.e. US/Pacific zone so
        #       we need to parse the timestamp like we are in that zone to get
        #       the same dates they get.
        date = date_from_timestamp(
            row.get("submission", {}).get("created", None), tz="US/Pacific"
        )

        description = row.get("submission", {}).get("description", "").strip()
        # This peace of a the code is taken from gulpfile.js translated to py
        model_name = description[: description.rfind("(")].strip()
        # _first_part = description[: description.rfind("(") + 1]
        # _institution = _first_part[: _first_part.rfind(")")]
        if description.rfind("http") != -1:
            link = description[description.rfind("http") :].strip()
        else:
            link = ""

        auroc = row.get("scores", {}).get("average_auroc", None)
        num_rads = row.get("scores", {}).get(
            "average_num_rads_under_roc", None
        )
        # Skip rows with no values
        if auroc is None or num_rads is None:
            continue

        sota_rows.append(
            SotaRow(
                model_name=model_name,
                paper_title=link,
                paper_url=link,
                paper_date=date,
                metrics={
                    "AVERAGE AUC ON 14 LABEL": sround(auroc, 3),
                    "NUM RADS BELOW CURVE": sround(num_rads, 3),
                },
            )
        )
    return sota_rows


def chexpert() -> TaskDB:
    """Extract CheXpert SOTA tables."""
    try:
        data = requests.get(JSON_URL).json()
    except Exception as e:
        raise HttpClientError(message=str(e))

    dataset = Dataset(name=DATASET_NAME, is_subdataset=False,)
    task = Task(name=TASK_NAME)
    task.datasets = [dataset]
    task.source_link = Link(title="CheXpert Leaderboard", url=URL)

    # scrape the evaluation values on the two datasets
    dataset.sota.metrics = ["AVERAGE AUC ON 14 LABEL", "NUM RADS BELOW CURVE"]

    dataset.sota.rows = get_sota_rows(data)

    tdb = TaskDB()
    tdb.add_task(task)
    return tdb
