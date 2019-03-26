import io
import csv
import json
from typing import Dict, List, Optional
from sota_extractor.taskdb.v01.models import Task, Dataset
from sota_extractor.taskdb.v01.schemas import TaskSchema


class TaskDB:
    def __init__(self):
        self.tasks = {}
        self.schema = TaskSchema()

    def get_task(self, name: str) -> Optional[Task]:
        """Get a task or a sub-task by name."""
        if name in self.tasks:
            return self.tasks[name]
        else:
            for task in self.tasks.values():
                for subtask in task.subtasks:
                    if subtask.name == name:
                        return subtask
        return None

    def add_task(self, task: Task):
        """Add a top-level task by name."""
        self.tasks[task.name] = task

    def load_tasks(self, json_files: List[str]):
        """Load tasks from a list of paths to JSON Files."""
        for json_file in json_files:
            with io.open(json_file, "r") as f:
                task_list = self.schema.load(json.load(f), many=True)
                for task in task_list:
                    self.add_task(task)

    def load_synonyms(self, csv_files: List[str]):
        """Load task synonyms from input files."""
        for csv_file in csv_files:
            with io.open(csv_file, newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    task = self.get_task(row[0])
                    if task is not None:
                        task.synonyms.append(row[1])

    def tasks_with_sota(self) -> List[Task]:
        """Extract all tasks with SOTA tables.

        This includes both the top-level and sub-tasks.
        """
        sota_tasks = []
        for task in self.tasks.values():
            find_sota_tasks(task, sota_tasks)
        return sota_tasks

    def datasets_with_sota(self) -> List[Dataset]:
        """Extract all datasets with SOTA tables.

        This includes both the top-level and sub-tasks.
        """

        sota_datasets = []

        for task in self.tasks.values():
            find_sota_datasets(task, sota_datasets)
        return sota_datasets

    def export(self) -> List[Dict]:
        """Export the whole of TaskDB into a list of tasks in Dict format."""
        return self.schema.dump(self.tasks.values(), many=True)

    def export_to_json(self, json_filename: str):
        """Export the whole of TaskDB into a JSON file."""
        with io.open(json_filename, "w") as f:
            json.dump(self.export(), f, indent=2, sort_keys=True)


def find_sota_tasks(task: Task, out: List):
    """Get all the tasks with a SOTA table.

    These tasks will be added into the "out" output list.
    """
    # check if the dataset has sota tables
    add = False
    for d in task.datasets:
        if d.sota.rows:
            add = True

        for sd in d.subdatasets:
            if sd.sota.rows:
                add = True
    if add:
        out.append(task)

    for subtask in task.subtasks:
        find_sota_tasks(subtask, out)


def find_sota_datasets(task: Task, out: List):
    """Get all the datasets with a SOTA table.

    These datasets will be added into the "out" output list.
    """

    # check if the dataset has sota tables
    add = False
    for d in task.datasets:
        if d.sota.rows:
            add = True

        for sd in d.subdatasets:
            if sd.sota.rows:
                add = True

        if add:
            out.append(d)

    for subtask in task.subtasks:
        find_sota_datasets(subtask, out)
