import pprint
import json
import re
import gzip
from extractor.taskdb import *
from nltk.stem.snowball import SnowballStemmer

# load the tasks and arxiv metadata

stemmer = SnowballStemmer("english")

TaskDb.load_tasks(["data/tasks/nlpprogress.json"])
with gzip.open("data/arxiv_metadata.json.gz") as f:
    arxiv = json.load(f)

# require and normalise arxiv titles
arxiv = [a for a in arxiv if "title" in a and a["title"] is not None]
for a in arxiv:
    a["title"] = re.sub(" +", " ", a["title"].replace("\n", " "))
    a["title_lower"] = a["title"].lower()
    a["abstract_lower"] = a["abstract"].lower()
    a["title_stem"] = stemmer.stem(a["title"])
    a["abstract_stem"] = stemmer.stem(a["abstract"])

# choose a task, and make predictions
task = TaskDb.get_task("Dependency parsing")
# FIXME: second table is for reference only
task.datasets[0].subdatasets = [task.datasets[0].subdatasets[0]]

query = task.task.lower()


def article_matches(paper, task, stemmer):
    """
    See if a paper mentions the tasks

    By mentioning it in the title or abstract
    And also mentioning state-of-the-art

    :param paper:
    :param task:
    :param stemmer:
    :return:
    """

    t = task.task.lower()
    ts = stemmer.stem(task.task)
    title = paper["title_lower"]
    abstract = paper["abstract_lower"]
    title_stem = paper["title_stem"]
    abstract_stem = paper["abstract_stem"]

    matches_paper = t in title or t in abstract or ts in title_stem or ts in abstract_stem

    contains_sota = "state-of-the-art" in abstract or "state-of-art" in abstract or \
        "state of the art" in abstract or "state of art" in abstract or "sota" in abstract

    return matches_paper and contains_sota


def eval_task(predicted:List[Dict], task:Task):
    """
    Get the precision and recall for a task, using any dataset

    :param predicted: The set of predicted true positive papers
    :param task: The task we are doing predictions against
    :return:
    """

    all_sota = []
    for d in task.datasets:
        all_sota.extend(d.sota_rows)
        for sd in d.subdatasets:
            all_sota.extend(sd.sota_rows)

    # true positives
    tp = []
    tp_sota = []
    for p in predicted:
        for s in all_sota:
            if p["arxiv_id"] in s.paper_url or p["title_lower"] == s.paper_title.lower():
                tp.append(p)
                tp_sota.append(s)

    fn = [s for s in all_sota if s not in tp_sota]
    fp = [p for p in predicted if p not in tp]

    return tp, fn, fp

pred = [a for a in arxiv if article_matches(a, task, stemmer)]

tp, fn, fp = eval_task(pred, task)
print(len(tp), len(fn), len(fp))
print("True positives")
pprint.pprint([p["title"] for p in tp], width=120)
print("------------")
print("False negatives")
pprint.pprint([s.paper_title for s in fn], width=120)
print("------------")
print("All `false positives`:")
pprint.pprint([p["title"] for p in fp], width=120)

