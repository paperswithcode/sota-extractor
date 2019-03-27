import re
import click
import pandas as pd
from typing import List, Dict
from nltk.stem.porter import PorterStemmer
from sota_extractor import serialization
from sota_extractor.commands.cli import cli
from sota_extractor.errors import catch_errors
from sota_extractor.taskdb.v01 import Task, TaskDB


def load(tdb):
    # load the tasks and arxiv metadata
    stemmer = PorterStemmer()

    tdb.load_tasks("data/tasks/nlpprogress.json")
    tdb.load_synonyms(["data/tasks/synonyms.csv"])
    arxiv = serialization.load(
        "data/arxiv_aclweb.json.gz", fmt=serialization.Format.json_gz
    )

    for a in arxiv:
        if a["abstract"] is None:
            a["abstract"] = ""

    # require and normalise arxiv titles
    arxiv = [a for a in arxiv if "title" in a and a["title"] is not None]
    for a in arxiv:
        a["title"] = re.sub(" +", " ", a["title"].replace("\n", " "))
        a["title_lower"] = a["title"].lower()
        a["abstract_lower"] = a["abstract"].lower()
        a["title_stem"] = stemmer.stem(a["title"])
        a["abstract_stem"] = stemmer.stem(a["abstract"])

    return arxiv


def eval_task(predicted: List[Dict], task: Task):
    """Get the precision and recall for a task, using any dataset.

    Args:
        predicted: The set of predicted true positive papers.
        task: The task we are doing predictions against.
    """

    all_sota = []
    for d in task.datasets:
        all_sota.extend(d.sota.rows)
        for sd in d.subdatasets:
            all_sota.extend(sd.sota.rows)

    # true positives
    tp = []
    tp_sota = []
    for p in predicted:
        for s in all_sota:
            if (
                p["arxiv_id"] and s.paper_url and p["arxiv_id"] in s.paper_url
            ) or (
                p["title_lower"]
                and s.paper_title
                and p["title_lower"] == s.paper_title.lower()
            ):
                tp.append(p)
                tp_sota.append(s)

    fn = [s for s in all_sota if s not in tp_sota]
    fp = [p for p in predicted if p not in tp]

    return tp, fn, fp


def article_matches(paper: Dict, task: Task):
    """Check if a paper mentions the tasks.

    By mentioning it in the title or abstract.
    And also mentioning state-of-the-art.
    """

    title = paper["title_lower"]
    abstract = paper["abstract_lower"]

    all_task_names = [task.name]
    all_task_names.extend(task.synonyms)

    matches_paper = False
    for task_name in all_task_names:
        task_name_lower = task_name.lower()
        matches_paper = matches_paper or task_name_lower in title
        matches_paper = matches_paper or task_name_lower in abstract

    contains_sota = (
        "state-of-the-art" in abstract
        or "state-of-art" in abstract
        or "state of the art" in abstract
        or "state of art" in abstract
        or "sota" in abstract
    )

    return matches_paper and contains_sota


def eval_all(tdb, arxiv, output):
    sota_tasks = tdb.tasks_with_sota()

    df = pd.DataFrame(
        columns=["task", "parent", "tp", "fn", "fp", "precision", "recall"]
    )

    for task in sota_tasks:
        pred = [a for a in arxiv if article_matches(a, task)]
        tp, fn, fp = eval_task(pred, task)

        prec = 0
        recal = 0
        if (len(tp) + len(fp)) != 0:
            prec = len(tp) / (len(tp) + len(fp))
        if len(tp) / (len(tp) + len(fn)) != 0:
            recal = len(tp) / (len(tp) + len(fn))

        parent = ""
        if task.parent:
            parent = task.parent.name

        df = df.append(
            {
                "task": task.name,
                "parent": parent,
                "tp": len(tp),
                "fn": len(fn),
                "fp": len(fp),
                "precision": round(prec, 2),
                "recall": round(recal, 2),
            },
            ignore_index=True,
        )

    df = df.append(
        {
            "task": "",
            "parent": "Total",
            "tp": round(df["tp"].mean(), 2),
            "fn": round(df["fn"].mean(), 2),
            "fp": round(df["fp"].mean(), 2),
            "precision": round(df["precision"].mean(), 2),
            "recall": round(df["recall"].mean(), 2),
        },
        ignore_index=True,
    )

    click.echo(f"Writing report into: {output}")
    df.to_csv(output)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/eval_all_report.csv",
    help="Output filename to use.",
)
@catch_errors
def evaluate(output):
    """Evaluate."""
    tdb = TaskDB()
    arxiv = load(tdb)
    eval_all(tdb, arxiv, output)
