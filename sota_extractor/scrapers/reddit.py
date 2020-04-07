import re
import requests
from bs4 import BeautifulSoup
from sota_extractor.taskdb.v01 import (
    Task,
    Dataset,
    Link,
    Sota,
    SotaRow,
    TaskDB,
)

REDITSOTA_URL = (
    "https://raw.githubusercontent.com/RedditSota/"
    "state-of-the-art-result-for-machine-learning-problems/master/README.md"
)


def reddit() -> TaskDB:
    """Extract Reddit SOTA tables."""
    tdb = TaskDB()
    md = requests.get(REDITSOTA_URL).text

    # assumptions:
    # ### Category
    # #### Task
    md_lines = md.split("\n")

    category = None
    task = None
    for i in range(len(md_lines)):
        line = md_lines[i]

        if line.startswith("###") and not line.startswith("####"):
            category = line.replace("###", "").strip()

        if line.startswith("####") and not line.startswith("#####"):
            task = line.replace("####", "").strip()
            task = re.sub("^[0-9+].?", "", task).strip()

        if "<table>" in line.lower():
            end_i = None
            # find the end of table
            for j in range(i, len(md_lines)):
                if "</table>" in md_lines[j].lower():
                    end_i = j + 1
                    break

            if end_i and task and category:
                html_lines = md_lines[i:end_i]
                h = "\n".join(html_lines)

                soup = BeautifulSoup(h, "html.parser")

                # parse out the individual rows
                entries = []
                rows = soup.findAll("tr")
                for row in rows:
                    cells = row.findAll("td")
                    if len(cells) >= 4:
                        # paper ref
                        c_paper = cells[0]
                        paper_title = c_paper.text.strip()
                        paper_url = None
                        if c_paper.find("a"):
                            paper_url = c_paper.find("a")["href"]

                        # datasets
                        c_datasets = cells[1]
                        c_datasets_li = c_datasets.findAll("li")
                        dataset_names = []
                        for dataset_li in c_datasets_li:
                            dataset_names.append(dataset_li.text.strip())

                        # metrics
                        c_metrics = cells[2]
                        c_metrics_li = c_metrics.findAll("li")
                        metrics = []
                        for metrics_li in c_metrics_li:
                            parts = metrics_li.text.split(":")
                            parts = [p.strip() for p in parts]
                            m = {}
                            if len(parts) == 2:
                                m[parts[0]] = parts[1]
                                metrics.append(m)

                        if not metrics:
                            # Try to use it as single value
                            parts = c_metrics.text.split(":")
                            parts = [p.strip() for p in parts]
                            m = {}
                            if len(parts) == 2:
                                m[parts[0]] = parts[1]
                                metrics.append(m)

                        # source code ref
                        c_code = cells[3]
                        c_code_a = c_code.findAll("a")
                        code_links = []
                        for code_a in c_code_a:
                            code_links.append(
                                Link(
                                    title=code_a.text.strip(),
                                    url=code_a["href"],
                                )
                            )

                        entries.append(
                            {
                                "paper_title": paper_title,
                                "paper_url": paper_url,
                                "dataset_names": dataset_names,
                                "metrics": metrics,
                                "code_links": code_links,
                            }
                        )

                # Add the new task
                t = Task(name=task, categories=[category])
                t.source_link = Link(title="RedditSota", url=REDITSOTA_URL)

                # Add datasets and perfomance on them
                data_map = {}
                for e in entries:
                    if len(e["dataset_names"]) == len(e["metrics"]):
                        for j in range(len(e["dataset_names"])):
                            dataset_name = e["dataset_names"][j]
                            # make sure the dataset exists
                            if dataset_name not in data_map:
                                # collect all the metrics mentioned for this
                                # dataset
                                all_metrics = [
                                    list(ee["metrics"][j].keys())
                                    for ee in entries
                                    if dataset_name in ee["dataset_names"]
                                ]
                                all_metrics = [
                                    item
                                    for sublist in all_metrics
                                    for item in sublist
                                ]
                                all_metrics = list(set(all_metrics))
                                dataset = Dataset(
                                    name=dataset_name,
                                    is_subdataset=False,
                                    sota=Sota(metrics=all_metrics),
                                )
                                data_map[dataset_name] = dataset
                                t.datasets.append(dataset)
                            else:
                                dataset = data_map[dataset_name]

                            # record the metric for this dataset
                            sr = SotaRow(
                                model_name="",
                                paper_title=e["paper_title"],
                                paper_url=e["paper_url"],
                                metrics=e["metrics"][j],
                                code_links=e["code_links"],
                            )
                            dataset.sota.rows.append(sr)

                # add and reset the task
                tdb.add_task(t)
                task = None

    return tdb
