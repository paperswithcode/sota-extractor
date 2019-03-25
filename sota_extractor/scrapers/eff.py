import click
from sota_extractor.scrapers.cli import cli
from sota_extractor.taskdb import Task, Dataset, Link, SotaRow, TaskDb
import requests
import json
from sota_extractor.scrapers.consts import EFF_TASK_CONVERSION


EFF_URL = (
    "https://raw.githubusercontent.com/AI-metrics/AI-metrics/master/"
    "export-api/v01/progress.json"
)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/eff.json",
    help="Output JSON filename to use.",
)
def eff(output):
    """Extract EFF SOTA tables."""

    json_raw = requests.get(EFF_URL)
    j = json.loads(json_raw.text)

    for problem in j["problems"]:

        if problem["name"] in EFF_TASK_CONVERSION:
            problem_name = EFF_TASK_CONVERSION[problem["name"]]
        else:
            problem_name = problem["name"]

        task = Task({"task": problem_name})

        task.source_link = Link(
            {
                "title": "Progress of AI Research",
                "url": "https://github.com/AI-metrics/AI-metrics",
            }
        )

        datasets = []
        for metric in problem["metrics"]:
            if "measures" in metric and metric["measures"]:
                measures = metric["measures"]

                dataset = Dataset(
                    {
                        "dataset": metric["name"],
                        "sota": {"metrics": [metric["scale"]]},
                    }
                )

                for measure in measures:
                    sr = SotaRow(
                        {
                            "model_name": measure["name"],
                            "paper_title": measure["papername"],
                            "paper_url": measure["url"],
                            "metrics": {metric["scale"]: measure["value"]},
                        }
                    )

                    if measure["replicated_url"]:
                        sr.code_links.append(
                            Link(
                                {
                                    "title": "Replicated",
                                    "url": measure["replicated_url"],
                                }
                            )
                        )

                    dataset.sota_rows.append(sr)

                datasets.append(dataset)

        task.datasets = datasets
        TaskDb.add_task(task.task, task)

    TaskDb.export_to_json(output)
