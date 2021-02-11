from datetime import datetime

import pytz
import requests

from sota_extractor.errors import HttpClientError
from sota_extractor.taskdb.v01 import SotaRow, Dataset, Task, Link, TaskDB


COQA_URL = "https://stanfordnlp.github.io/coqa/"
COQA_JSON_URL = (
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
        model_name = description[0 : description.rfind("(")].strip()
        # _first_part = description[description.rfind("(") + 1 :]
        # _institution = _first_part[0 : _first_part.rfind(")")]
        if description.rfind("http") != -1:
            link = description[description.rfind("http") :].strip()
        else:
            link = ""

        in_domain = row.get("scores", {}).get("in_domain_f1", 0)
        out_of_domain = row.get("scores", {}).get("out_of_domain_f1", 0)
        overall = row.get("scores", {}).get("overall_f1", 0)

        sota_rows.append(
            SotaRow(
                model_name=model_name,
                paper_title=link,
                paper_url=link,
                paper_date=date,
                metrics={
                    "IN-DOMAIN": in_domain,
                    "OUT-OF-DOMAIN": out_of_domain,
                    "OVERALL": overall,
                },
            )
        )
    return sota_rows


def coqa() -> TaskDB:
    """Extract SQUAD SOTA tables."""
    try:
        coqa = requests.get(COQA_JSON_URL).json()
    except Exception as e:
        raise HttpClientError(message=str(e))

    dataset = Dataset(name=DATASET_NAME, is_subdataset=False,)
    task = Task(name=TASK_NAME)
    task.datasets = [dataset]
    task.source_link = Link(title="CoQA Leaderboard", url=COQA_URL)

    # scrape the evaluation values on the two datasets
    dataset.sota.metrics = ["IN-DOMAIN", "OUT-OF-DOMAIN", "OVERALL"]

    dataset.sota.rows = get_sota_rows(coqa)

    tdb = TaskDB()
    tdb.add_task(task)
    return tdb
