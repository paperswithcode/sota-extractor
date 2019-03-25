from typing import Dict, List
from sota_extractor.taskdb import Task


def eval_task(predicted: List[Dict], task: Task):
    """Get the precision and recall for a task, using any dataset.

    Args:
        predicted: The set of predicted true positive papers.
        task: The task we are doing predictions against.
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
