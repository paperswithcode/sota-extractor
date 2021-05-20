import re

import requests

from sota_extractor.errors import HttpClientError
from sota_extractor.scrapers.utils import date_from_timestamp, sround
from sota_extractor.taskdb.v01 import SotaRow, Dataset, Task, Link, TaskDB


URL = "https://hotpotqa.github.io/"
JSON_URL = (
    "https://raw.githubusercontent.com/hotpotqa/hotpotqa.github.io/master/"
    "leaderboard-utils/fullwiki-leaderboard.json"
)

TASK_NAME = "Question Answering"
DATASET_NAME = "HotpotQA"


def get_sota_rows(data):
    rows = data["leaderboard"]

    sota_rows = []
    for row in rows:
        # FIXME: The generation of the page uses local timezone and there are a
        #        couple of them that match the current state but I have no idea
        #        which is the correct one.
        date = date_from_timestamp(
            row.get("submission", {}).get("created", None)
        )

        description = row.get("submission", {}).get("description", "").strip()
        # This peace of a the code is taken from gulpfile.js translated to py
        model_name = description[: description.find("(")].strip()
        match = re.search(r"\[(.*?)\]\s*\((.*?)\)", description)
        if match is not None:
            paper, link = match.groups()
            paper = paper.strip().strip("()").strip()
            link = link.strip()
        else:
            paper = ""
            link = ""

        ans_em = row.get("scores", {}).get("ans_em", None)
        ans_f1 = row.get("scores", {}).get("ans_f1", None)
        sup_em = row.get("scores", {}).get("sup_em", None)
        sup_f1 = row.get("scores", {}).get("sup_f1", None)
        joint_em = row.get("scores", {}).get("joint_em", None)
        joint_f1 = row.get("scores", {}).get("joint_f1", None)

        # Skip rows with no values
        if (
            ans_em is None
            or ans_f1 is None
            or sup_em is None
            or sup_f1 is None
            or joint_em is None
            or joint_f1 is None
        ):
            continue

        sota_rows.append(
            SotaRow(
                model_name=model_name,
                paper_title=paper,
                paper_url=link,
                paper_date=date,
                metrics={
                    "ANS-EM": sround(ans_em, 3),
                    "ANS-F1": sround(ans_f1, 3),
                    "SUP-EM": sround(sup_em, 3),
                    "SUP-F1": sround(sup_f1, 3),
                    "JOINT-EM": sround(joint_em, 3),
                    "JOINT-F1": sround(joint_f1, 3),
                },
            )
        )
    return sota_rows


def hotpotqa() -> TaskDB:
    """Extract HotpotQA SOTA tables."""
    try:
        data = requests.get(JSON_URL).json()
    except Exception as e:
        raise HttpClientError(message=str(e))

    dataset = Dataset(name=DATASET_NAME, is_subdataset=False,)
    task = Task(name=TASK_NAME)
    task.datasets = [dataset]
    task.source_link = Link(title="HotpotQA Leaderboard", url=URL)

    # scrape the evaluation values on the two datasets
    dataset.sota.metrics = [
        "ANS-EM",
        "ANS-F1",
        "SUP-EM",
        "SUP-F1",
        "JOINT-EM",
        "JOINT-F1",
    ]

    dataset.sota.rows = get_sota_rows(data)

    tdb = TaskDB()
    tdb.add_task(task)
    return tdb
