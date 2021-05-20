from datetime import datetime

import requests

from sota_extractor.scrapers.utils import sround
from sota_extractor.errors import HttpClientError
from sota_extractor.taskdb.v01 import SotaRow, Dataset, Task, Link, TaskDB


URL_2018 = "http://ymcui.com/cmrc2018/"
URL_2019 = "http://ymcui.com/cmrc2019/"

CMRC_2018_JSON_URL = (
    "https://raw.githubusercontent.com/ymcui/cmrc2018/gh-pages/docs/"
    "raw_score.json"
)
CMRC_2019_JSON_URL = (
    f"https://raw.githubusercontent.com/ymcui/cmrc2019/gh-pages/docs/"
    f"raw_score.json"
)

TASK_NAME = "Chinese Reading Comprehension"
DATASET_2018_NAME = "CMRC 2018 (Chinese Machine Reading Comprehension 2018)"
DATASET_2019_NAME = "CMRC 2019 (Chinese Machine Reading Comprehension 2019)"


def get_sota_rows(data):
    sota_rows = []

    if data["version"] == "cmrc2018":
        for row in data["data"]:
            try:
                date = datetime.strptime(row.get("date", ""), "%b %d, %Y")
            except ValueError:
                date = None

            model_name = row.get("system_name", "").strip()
            model_type = row.get("model_type", "").strip()
            if model_type != "":
                model_name = f"{model_name} ({model_type})"

            test_em = row.get("test_em", None)
            test_f1 = row.get("test_f1", None)
            challenge_em = row.get("challenge_em", None)
            challenge_f1 = row.get("challenge_f1", None)

            # Skip rows with no values
            if (
                test_em is None
                or test_f1 is None
                or challenge_em is None
                or challenge_f1 is None
            ):
                continue

            sota_rows.append(
                SotaRow(
                    model_name=model_name,
                    paper_title=row["paper"],
                    paper_url="" if row["url"] == "-" else row["url"],
                    paper_date=date,
                    metrics={
                        "TEST-EM": sround(test_em, 3),
                        "TEST-F1": sround(test_f1, 3),
                        "CHALLENGE-EM": sround(challenge_em, 3),
                        "CHALLENGE-F1": sround(challenge_f1, 3),
                    },
                )
            )

    elif data["version"] == "cmrc2019":
        for row in data["data"]:
            try:
                date = datetime.strptime(row.get("date", ""), "%Y/%m/%d")
            except ValueError:
                date = None

            model_name = row.get("system_name", "").strip()
            model_type = row.get("model_type", "").strip()
            if model_type != "":
                model_name = f"{model_name} ({model_type})"

            sota_rows.append(
                SotaRow(
                    model_name=model_name,
                    paper_title=row["url"],
                    paper_url=row["url"],
                    paper_date=date,
                    metrics={
                        "QAC": str(row.get("test_qac", 0)),
                        "PAC": str(row.get("test_pac", 0)),
                    },
                )
            )

    return sota_rows


def cmrc() -> TaskDB:
    """Extract CMRC SOTA tables."""
    try:
        cmrc_2018 = requests.get(CMRC_2018_JSON_URL).json()
        cmrc_2019 = requests.get(CMRC_2019_JSON_URL).json()
    except Exception as e:
        raise HttpClientError(message=str(e))

    dataset_2018 = Dataset(
        name=DATASET_2018_NAME,
        is_subdataset=False,
        links=[Link("CMRC 2018 Leadergboard", url=URL_2018)],
    )
    dataset_2019 = Dataset(
        name=DATASET_2019_NAME,
        is_subdataset=False,
        links=[Link("CMRC 2019 Leadergboard", url=URL_2019)],
    )

    task = Task(name=TASK_NAME)

    task.datasets = [dataset_2018, dataset_2019]

    # scrape the evaluation values on the two datasets
    dataset_2018.sota.metrics = [
        "TEST-EM",
        "TEST-F1",
        "CHALLENGE-EM",
        "CHALLENGE-F1",
    ]
    dataset_2019.sota.metrics = ["QAC", "PAC"]

    dataset_2018.sota.rows = get_sota_rows(cmrc_2018)
    dataset_2019.sota.rows = get_sota_rows(cmrc_2019)

    tdb = TaskDB()
    tdb.add_task(task)
    return tdb
