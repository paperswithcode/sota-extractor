import argparse
from extractor.taskdb import *
import requests
import json

from .consts import EFF_TASK_CONVERSION

parser = argparse.ArgumentParser()
parser.add_argument("--out", default="data/tasks/eff.json", help="Output JSON filename to use")
args = parser.parse_args()

URL = "https://raw.githubusercontent.com/AI-metrics/AI-metrics/master/export-api/v01/progress.json"
out_filename = args.out

json_raw = requests.get(URL)
j = json.loads(json_raw.text)

for problem in j["problems"]:

    if problem["name"] in EFF_TASK_CONVERSION:
        problem_name = EFF_TASK_CONVERSION[problem["name"]]
    else:
        problem_name = problem["name"]

    task = Task({"task": problem_name})

    task.source_link = Link({"title": "Progress of AI Research", "url": "https://github.com/AI-metrics/AI-metrics"})

    datasets = []
    for metric in problem["metrics"]:
        if "measures" in metric and metric["measures"]:
            measures = metric["measures"]

            dataset = Dataset({"dataset": metric["name"], "sota": {"metrics": [metric["scale"]]}})

            for measure in measures:
                m = {}
                m[metric["scale"]] = measure["value"]
                sr = SotaRow({
                    "model_name": measure["name"],
                    "paper_title": measure["papername"],
                    "paper_url": measure["url"],
                    "metrics": m,
                })

                if measure["replicated_url"]:
                    sr.code_links.append(Link({"title": "Replicated", "url": measure["replicated_url"]}))

                dataset.sota_rows.append(sr)

            datasets.append(dataset)

    task.datasets = datasets
    TaskDb.add_task(task.task, task)


TaskDb.export_to_json(out_filename)