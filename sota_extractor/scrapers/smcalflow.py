from datetime import datetime

import pytz
import requests

from sota_extractor.errors import HttpClientError
from sota_extractor.taskdb.v01 import SotaRow, Dataset, Task, Link, TaskDB


URL = (
    "https://microsoft.github.io/task_oriented_dialogue_as_dataflow_synthesis/"
)
JSON_URL = (
    "https://raw.githubusercontent.com/microsoft/"
    "task_oriented_dialogue_as_dataflow_synthesis/leaderboard/out-v2.0.json"
)

TASK_NAME = "Task-Oriented Dialogue as Dataflow Synthesis"
DATASET_NAME = "SMCalFlow"


def get_sota_rows(data):
    rows = data["leaderboard"]

    sota_rows = []
    for row in rows:
        description = row.get("submission", {}).get("description", "").strip()
        if description == "":
            continue

        date = row.get("submission", {}).get("created", None)
        if isinstance(date, int):
            # HACK: This hack with the timezone is needed because the person
            #       who maintains the leaderboard uses local timezone. He just
            #       runs the gulp html generation script in (from github
            #       profile) Berkeley which is in the US/Pacific zone so we
            #       need to parse the timestamp like we are in that zone to get
            #       the same dates they get.
            date = datetime.fromtimestamp(
                date, pytz.timezone("US/Pacific")
            ).replace(tzinfo=pytz.utc)

        # This peace of a the code is taken from gulpfile.js translated to py
        model_name = description[: description.rfind("(")].strip()
        # _first_part = description[description.rfind("(") + 1 :]
        # _institution = _first_part[: _first_part.rfind(")")]
        if description.rfind("http") != -1:
            link = description[description.rfind("http") :].strip()
        else:
            link = ""

        sota_rows.append(
            SotaRow(
                model_name=model_name,
                paper_title=link,
                paper_url=link,
                paper_date=date,
                metrics={
                    "Accuracy": str(row.get("scores", {}).get("accuracy", 0)),
                },
            )
        )
    return sota_rows


def smcalflow() -> TaskDB:
    """Extract SMCalFlow SOTA tables."""
    try:
        data = requests.get(JSON_URL).json()
    except Exception as e:
        raise HttpClientError(message=str(e))

    dataset = Dataset(name=DATASET_NAME, is_subdataset=False,)
    task = Task(name=TASK_NAME)
    task.datasets = [dataset]
    task.source_link = Link(title="SMCalFlow Leaderboard", url=URL)

    # scrape the evaluation values on the two datasets
    dataset.sota.metrics = ["Accuracy"]

    dataset.sota.rows = get_sota_rows(data)

    tdb = TaskDB()
    tdb.add_task(task)
    return tdb
