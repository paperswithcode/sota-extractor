import re
from datetime import datetime

import pytz
import requests

from sota_extractor.errors import HttpClientError
from sota_extractor.taskdb.v01 import SotaRow, Dataset, Task, Link, TaskDB


SQUAD_URL = "https://rajpurkar.github.io/SQuAD-explorer/"
SQUAD_MASTER_URL = (
    "https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master"
)
SQUAD_1_1_JSON_URL = f"{SQUAD_MASTER_URL}/out-v1.1.json"
SQUAD_2_0_JSON_URL = f"{SQUAD_MASTER_URL}/out-v2.0.json"

TASK_NAME = "Question Answering"
DATASET_1_NAME = "SQuAD1.1"
DATASET_1_DESCRIPTION = (
    "Previous version of the SQuAD2.0 dataset with 50,000 question-answer "
    "pairs."
)
DATASET_2_NAME = "SQuAD2.0"
DATASET_2_DESCRIPTION = (
    "Stanford Question Answering Dataset (SQuAD) is a reading comprehension "
    "dataset, consisting of questions posed by crowdworkers on a set of "
    "Wikipedia articles, where the answer to every question is a segment of "
    "text, or span, from the corresponding reading passage, or the question "
    "might be unanswerable."
)


def get_sota_rows(data):
    rows = data["leaderboard"]

    sota_rows = []
    for row in rows:
        date = row.get("submission", {}).get("created", None)
        if isinstance(date, int):
            # HACK: This hack with the timezone is needed because they don't
            #       use timezones. They just run the gulp html generation
            #       script in localtime which is (I guess) Stanford i.e.
            #       US/Pacific zone so we need to parse the timestamp like we
            #       are in that zone to get the same dates they get.
            date = datetime.fromtimestamp(
                date, pytz.timezone("US/Pacific")
            ).replace(tzinfo=pytz.utc)

        description = row.get("submission", {}).get("description", "").strip()
        # This peace of a the code is taken from gulpfile.js translated to py
        regex_match = re.match(r"(.*?) ?\((.*?)\) ?\((.*?)\)(.*)", description)
        if regex_match is not None:
            groups = regex_match.groups()
            model_name = f"{groups[0].strip()} ({groups[1].strip()})"
            # _institution = groups[2].strip()
            if groups[3].find("http") != -1:
                link = groups[3].strip()
            else:
                link = ""
        else:
            model_name = description[: description.rfind("(")].strip()
            # _first_part = description[description.rfind("(") + 1 :]
            # _institution = _first_part[: _first_part.rfind(")")]
            if description.find("http") != -1:
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
                    "EM": str(row.get("scores", {}).get("exact_match", 0)),
                    "F1": str(row.get("scores", {}).get("f1", 0)),
                },
            )
        )
    return sota_rows


def squad() -> TaskDB:
    """Extract SQUAD SOTA tables."""
    try:
        squad_1 = requests.get(SQUAD_1_1_JSON_URL).json()
        squad_2 = requests.get(SQUAD_2_0_JSON_URL).json()
    except Exception as e:
        raise HttpClientError(message=str(e))

    dataset1 = Dataset(
        name=DATASET_1_NAME,
        is_subdataset=False,
        description=DATASET_1_DESCRIPTION,
    )
    dataset2 = Dataset(
        name=DATASET_2_NAME,
        is_subdataset=False,
        description=DATASET_2_DESCRIPTION,
    )
    task = Task(name=TASK_NAME)
    task.datasets = [dataset2, dataset1]
    task.source_link = Link(title="SQuAD Leaderboard", url=SQUAD_URL)

    # scrape the evaluation values on the two datasets
    dataset1.sota.metrics = ["EM", "F1"]
    dataset2.sota.metrics = ["EM", "F1"]

    dataset1.sota.rows = get_sota_rows(squad_1)
    dataset2.sota.rows = get_sota_rows(squad_2)

    tdb = TaskDB()
    tdb.add_task(task)
    return tdb
