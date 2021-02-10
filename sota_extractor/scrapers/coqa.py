from datetime import datetime

import pytz
import requests

from sota_extractor.errors import HttpClientError
from sota_extractor.taskdb.v01 import SotaRow, Dataset, Task, Link, TaskDB


URL = "https://stanfordnlp.github.io/coqa/"
JSON_URL = (
    "https://raw.githubusercontent.com/stanfordnlp/coqa/master/out-v1.0.json"
)

TASK_NAME = "Question Answering"
DATASET_NAME = "CoQA (Conversational Question Answering Challenge)"


def get_sota_rows(data):
    rows = data["leaderboard"]

    sota_rows = []
    for row in rows:
        date = row.get("submission", {}).get("created", None)
        if isinstance(date, str):
            try:
                date = int(date)
            except ValueError:
                pass
        if isinstance(date, int):
            # HACK: This hack with the timezone is needed because the person
            #       who maintains the leaderboard uses local timezone. He just
            #       runs the gulp html generation script in (from github
            #       profile) Montreal which is in the America/Montreal zone so
            #       we need to parse the timestamp like we are in that zone to
            #       get the same dates they get.
            date = datetime.fromtimestamp(
                date, pytz.timezone("America/Montreal")
            ).replace(tzinfo=pytz.utc)

        description = row.get("submission", {}).get("description", "").strip()
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
                    "IN-DOMAIN": str(
                        row.get("scores", {}).get("in_domain_f1", 0)
                    ),
                    "OUT-OF-DOMAIN": str(
                        row.get("scores", {}).get("out_of_domain_f1", 0)
                    ),
                    "OVERALL": str(row.get("scores", {}).get("overall_f1", 0)),
                },
            )
        )
    return sota_rows


def coqa() -> TaskDB:
    """Extract SQUAD SOTA tables."""
    try:
        coqa = requests.get(JSON_URL).json()
    except Exception as e:
        raise HttpClientError(message=str(e))

    dataset = Dataset(name=DATASET_NAME, is_subdataset=False,)
    task = Task(name=TASK_NAME)
    task.datasets = [dataset]
    task.source_link = Link(title="CoQA Leaderboard", url=URL)

    # scrape the evaluation values on the two datasets
    dataset.sota.metrics = ["IN-DOMAIN", "OUT-OF-DOMAIN", "OVERALL"]

    dataset.sota.rows = get_sota_rows(coqa)

    tdb = TaskDB()
    tdb.add_task(task)
    return tdb
