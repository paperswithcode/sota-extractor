import pprint
from sota_extractor.load import TaskDb


def test_datasets():
    datasets = TaskDb.datasets_with_sota()
    dataset_names = [d.dataset for d in datasets]
    print("Unique datasets: %d" % len(set(dataset_names)))
    pprint.pprint(dataset_names, width=120)
