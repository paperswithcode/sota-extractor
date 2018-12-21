import pprint
from extractor.load import TaskDb, arxiv, stemmer
from extractor.predict import article_matches
from extractor.eval import eval_task

datasets = TaskDb.datasets_with_sota()

dataset_names = [d.dataset for d in datasets]
print("Unique datasets: %d" % len(set(dataset_names)))
pprint.pprint(dataset_names, width=120)
