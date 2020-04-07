import io
import csv
from typing import Dict, List, Optional, Any

from sota_extractor.consts import Format
from sota_extractor.errors import ArgumentError
from sota_extractor.taskdb.v01.models import Task, Dataset
from sota_extractor.taskdb.v01.schemas import TaskSchema


class TaskDB:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
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

    def load_tasks(self, files: List[str] = None, data: List[Dict] = None):
        """Load tasks from files or from data.

        Args:
            files (List[str] | str): Path to a document or a list of paths to
                documents.
            data: Sota data - list of dictionaries representing tasks.
        """
        from sota_extractor.serialization import load

        if files is None and data is None:
            raise ArgumentError("Either 'files' or 'data' must be supplied.")

        if isinstance(files, str):
            files = [files]

        if files is not None:
            data = []
            for file in files:
                data.extend(load(file))

        task_list = self.schema.load(data, many=True)
        for task in task_list:
            self.add_task(task)

    def load_synonyms(self, csv_files: List[str]):
        """Load task synonyms from input files."""
        if isinstance(csv_files, str):
            csv_files = [csv_files]
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

    def export(self) -> List[Dict[str, Any]]:
        """Export the whole of TaskDB into a list of tasks in Dict format."""
        return self.schema.dump(self.tasks.values(), many=True)

    def export_to_file(self, filename: str, fmt=Format.json):
        """Export the whole of TaskDB into a file."""
        from sota_extractor.serialization import dump

        dump(self, filename=filename, fmt=fmt)


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
