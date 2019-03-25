import pprint
from sota_extractor.load import TaskDb, arxiv
from sota_extractor.predict import article_matches
from sota_extractor.eval import eval_task

# choose a task, and make predictions
task = TaskDb.get_task("Part-of-speech tagging")
# FIXME: second table is for reference only
# task.datasets[0].subdatasets = [task.datasets[0].subdatasets[0]]

pred = [a for a in arxiv if article_matches(a, task)]

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
