import json
import requests
from sota_extractor.errors import HttpClientError
from sota_extractor.consts import EFF_TASK_CONVERSION
from sota_extractor.taskdb.v01 import (
    Task,
    Dataset,
    Link,
    SotaRow,
    Sota,
    TaskDB,
)

EFF_URL = (
    "https://raw.githubusercontent.com/AI-metrics/AI-metrics/master/"
    "export-api/v01/progress.json"
)


def eff() -> TaskDB:
    """Extract EFF SOTA tables."""

    response = requests.get(EFF_URL)
    if response.status_code != 200:
        raise HttpClientError("Resource unavailable", response=response)
    j = json.loads(response.text)
    tdb = TaskDB()

    for problem in j["problems"]:

        if problem["name"] in EFF_TASK_CONVERSION:
            problem_name = EFF_TASK_CONVERSION[problem["name"]]
        else:
            problem_name = problem["name"]

        task = Task(name=problem_name)

        task.source_link = Link(
            title="Progress of AI Research",
            url="https://github.com/AI-metrics/AI-metrics",
        )

        datasets = []
        for metric in problem["metrics"]:
            if "measures" in metric and metric["measures"]:
                measures = metric["measures"]

                dataset = Dataset(
                    name=metric["name"],
                    is_subdataset=False,
                    sota=Sota(metrics=[metric["scale"]]),
                )

                for measure in measures:
                    sr = SotaRow(
                        model_name=measure["name"],
                        paper_title=measure["papername"],
                        paper_url=measure["url"],
                        metrics={metric["scale"]: measure["value"]},
                    )

                    if measure["replicated_url"]:
                        sr.code_links.append(
                            Link(
                                title="Replicated",
                                url=measure["replicated_url"],
                            )
                        )

                    dataset.sota.rows.append(sr)

                datasets.append(dataset)

        task.datasets = datasets
        tdb.add_task(task)

    return tdb
