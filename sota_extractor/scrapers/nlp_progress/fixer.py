from typing import Optional, List

from sota_extractor.taskdb.v01 import Task, Dataset


def fix_dataset(dataset: Dataset) -> Optional[Dataset]:
    """Walk through the dataset and return a valid one.

    Valid dataset contains only subdatasets with non empty sota tables or,
    if it has no subdatasets, its sota table has to be non-empty.
    """
    dataset.subdatasets = [
        subdataset
        for subdataset in dataset.subdatasets
        if len(subdataset.sota.rows) > 0
    ]

    if len(dataset.subdatasets) > 0:
        return dataset

    if len(dataset.sota.rows) > 0:
        return dataset

    return None


def fix_datasets(datasets: List[Dataset]) -> List[Dataset]:
    """Filter out invalid datasets."""
    return [
        dataset
        for dataset in [fix_dataset(dataset) for dataset in datasets]
        if dataset is not None
    ]


def fix_subtasks(subtasks: List[Task]) -> List[Task]:
    """Filter out invalid subtasks."""
    valid_subtasks = []

    for subtask in subtasks:
        subtask.datasets = fix_datasets(subtask.datasets)
        if len(subtask.datasets) > 0:
            valid_subtasks.append(subtask)

    return valid_subtasks


def fix_task(task: Task) -> Optional[Task]:
    """Return a valid task.

    To be a valid task it has to have a dataset with sota tables or a sub-task
    with dataset with a valid table.
    """
    task.datasets = fix_datasets(task.datasets)
    task.subtasks = fix_subtasks(task.subtasks)
    if len(task.datasets) > 0 or len(task.subtasks) > 0:
        return task

    return None
