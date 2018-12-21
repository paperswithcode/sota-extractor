import pprint
from extractor.load import TaskDb, arxiv, stemmer
from extractor.predict import article_matches
from extractor.eval import eval_task
import pandas
# find all tasks that have an attached SOTA table

sota_tasks = TaskDb.tasks_with_sota()

df = pandas.DataFrame(columns=['task', 'tp', 'fn', 'fp', 'precision', 'recall'])

for task in sota_tasks:
    pred = [a for a in arxiv if article_matches(a, task, stemmer)]
    tp, fn, fp = eval_task(pred, task)

    prec = 0
    recal = 0
    if (len(tp)+len(fp)) != 0:
        prec = len(tp) / (len(tp)+len(fp))
    if len(tp) / (len(tp)+len(fn)) != 0:
        recal = len(tp) / (len(tp)+len(fn))

    df = df.append({
        "task": task.task,
        "tp": len(tp),
        "fn": len(fn),
        "fp": len(fp),
        "precision": round(prec,2),
        "recall": round(recal,2),
    }, ignore_index=True)

df = df.append({
    "task": "Total",
    "tp": round(df["tp"].mean(),2),
    "fn": round(df["fn"].mean(),2),
    "fp": round(df["fp"].mean(),2),
    "precision": round(df["precision"].mean(),2),
    "recall": round(df["recall"].mean(),2),
}, ignore_index=True)

print("Writing report into `eval_all_report.csv`")
df.to_csv("eval_all_report.csv")

