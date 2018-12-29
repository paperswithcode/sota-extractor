from extractor.taskdb import Task
from extractor.load import TaskDb, arxiv, stemmer
from typing import Dict, Tuple, List


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
            if (p["arxiv_id"] and s.paper_url and p["arxiv_id"] in s.paper_url) or \
                    (p["title_lower"] and s.paper_title and p["title_lower"] == s.paper_title.lower()):
                tp.append(p)
                tp_sota.append(s)

    fn = [s for s in all_sota if s not in tp_sota]
    fp = [p for p in predicted if p not in tp]

    return tp, fn, fp