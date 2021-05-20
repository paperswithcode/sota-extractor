import re
import json
import _jsonnet
from datetime import datetime

import requests

from sota_extractor.taskdb.v01 import (
    Link,
    Task,
    Dataset,
    Sota,
    SotaRow,
    TaskDB,
)


XTREME_URL = "https://sites.research.google/xtreme/app.js"


REGEX = re.compile(
    r"""
    ^                                  # Start of the line
    \s*                                # Optional space
    passageLbList\.push\(              # Push to a list
        (?P<json>\{.*?\})              # JS object that's pushed
    \)\;                               # End of the push
    \s*                                # Optional space
    $                                  # End of the line
""",
    re.VERBOSE,
)


def xtreme() -> TaskDB:
    """Extract Xtreme SOTA tables."""
    data = requests.get(XTREME_URL).text.splitlines()

    sota_rows = []
    for line in data:
        match = REGEX.match(line)
        if match is not None:
            try:
                data = json.loads(
                    _jsonnet.evaluate_snippet(
                        "snippet", match.groupdict().get("json", "{}")
                    )
                )

                # Skip human performance
                if data["modelName"].strip() == "":
                    continue

                sota_rows.append(
                    SotaRow(
                        model_name=data["modelName"],
                        paper_title=data["participant"],
                        paper_url=data["referenceLink"],
                        paper_date=datetime.strptime(
                            data["date"], "%b %d, %Y"
                        ),
                        metrics={
                            "Avg": data["avgAllScoreString"],
                            "Sentence-pair Classification": data[
                                "avgSpcScoreString"
                            ],
                            "Structured Prediction": data["avgSpScoreString"],
                            "Question Answering": data["avgQaScoreString"],
                            "Sentence Retrieval": data["avgSrScoreString"],
                        },
                    )
                )
            except Exception:
                continue

    task = Task(
        name="Zero-Shot Cross-Lingual Transfer",
        datasets=[
            Dataset(
                name="XTREME",
                is_subdataset=False,
                sota=Sota(
                    metrics=[
                        "Avg",
                        "Sentence-pair Classification",
                        "Structured Prediction",
                        "Question Answering",
                        "Sentence Retrieval",
                    ],
                    rows=sota_rows,
                ),
            )
        ],
        source_link=Link(
            title=(
                "(X) Cross-Lingual Transfer Evaluation of Multilingual "
                "Encoders"
            ),
            url="https://sites.research.google/xtreme",
        ),
    )
    tdb = TaskDB()
    tdb.add_task(task)
    return tdb
