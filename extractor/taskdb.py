import json
import csv
from typing import Dict, Tuple, List

class Link:
    def __init__(self, d:Dict):
        """
        Make a new Link to a URL from the dictionary of values

        :param d: a dictionary with the data (from the JSON)
        """

        self.title = ""
        self.url = ""

        if "title" in d:
            self.title = d["title"]

        if "url" in d:
            self.url = d["url"]

class SotaRow:
    def __init__(self, d: Dict):
        """
        A row of the SOTA table

        :param d: a dictionary with the data (from the JSON)
        """

        self.model_name = d["model_name"]
        self.paper_title = ""
        self.paper_url = ""
        self.paper_date = None

        if "paper_title" in d:
            self.paper_title = d["paper_title"]

        if "paper_url" in d:
            self.paper_url = d["paper_url"]

        if "paper_date" in d:
            self.paper_date = d["paper_date"]

        self.code_links = []
        self.model_links = []

        if "code_links" in d:
            for code_d in d["code_links"]:
                if code_d:
                    self.code_links.append(Link(code_d))

        if "model_links" in d:
            for model_d in d["model_links"]:
                if model_d:
                    self.model_links.append(Link(model_d))

        self.metrics = d["metrics"]


class Dataset:
    def __init__(self, d:Dict, parent=None):
        """
        Make a new Dataset instance from a dictionary of values

        :param d: a dictionary with the data (from the JSON)
        :param parent: The parent dataset if present, i.e if the dataset is a subdataset
        """
        if "subdataset" in d:
            self.dataset = d["subdataset"]
        else:
            self.dataset = d["dataset"]
        self.description = ""
        if "description" in d:
            self.description = d["description"]

        self.parent = parent

        self.sota_metrics = []
        self.sota_rows = []

        if "sota" in d:
            if "metrics" in d["sota"]:
                self.sota_metrics = d["sota"]["metrics"]
            if "rows" in d["sota"]:
                for sota_row_d in d["sota"]["rows"]:
                    if sota_row_d:
                        self.sota_rows.append(SotaRow(sota_row_d))

        self.subdatasets = []
        if "subdatasets" in d:
            for subd_d in d["subdatasets"]:
                if subd_d:
                    self.subdatasets.append(Dataset(subd_d, parent=self))

        self.dataset_links = []
        if "dataset_links" in d:
            for link_d in d["dataset_links"]:
                if link_d:
                    self.dataset_links.append(Link(link_d))

        self.dataset_citations = []
        if "dataset_citations" in d:
            for link_d in d["dataset_citations"]:
                if link_d:
                    self.dataset_links.append(Link(link_d))


class Task:
    def __init__(self, d:Dict, parent=None):
        """
        Make a new Task from a dictionary of values

        :param d: a dictionary with all the data (from the JSON)
        :param parent: The parent Task (if any)
        """
        self.task = d["task"]
        self.description = ""
        if "description" in d:
            self.description = d["description"]
        self.parent = parent

        self.categories = []
        if "categories" in d:
            self.categories = d["categories"]

        self.datasets = []
        if "datasets" in d:
            for dataset_d in d["datasets"]:
                if dataset_d:
                    self.datasets.append(Dataset(dataset_d))

        self.subtasks = []
        if "subtasks" in d:
            for subt_d in d["subtasks"]:
                if subt_d:
                    self.subtasks.append(Task(subt_d, parent=self))

        self.synonyms = []


class TaskDb:
    tasks = {}

    @staticmethod
    def get_task(name:str):
        """
        Get a task or subtask by name

        :param name:
        :return:
        """
        if name in TaskDb.tasks:
            return TaskDb.tasks[name]
        else:
            for t in TaskDb.tasks.values():
                for subtask in t.subtasks:
                    if subtask.task == name:
                        return subtask
        return None

    @staticmethod
    def add_task(name:str, task:Task):
        """
        Add a top-level task by name

        :param name:
        :param task:
        :return:
        """
        TaskDb.tasks[name] = task

    @staticmethod
    def load_tasks(json_files: List[str]):
        """
        Load tasks from a list of paths to JSON Files

        :param json_files:
        :return:
        """
        for json_file in json_files:
            with open(json_file, "r") as f:
                task_list = json.load(f)
                for t in task_list:
                    TaskDb.add_task(t["task"], Task(t))


    @staticmethod
    def load_synonyms(csv_files: List[str]):
        """
        Load task synonyms from input files

        :param csv_files:
        :return:
        """

        for csv_file in csv_files:
            with open(csv_file, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    task = TaskDb.get_task(row[0])
                    if task is not None:
                        task.synonyms.append(row[1])

    @staticmethod
    def tasks_with_sota() -> List[Task]:
        """
        Extract all tasks with SOTA tables.
        This includes both the top-level and subtasks

        :return:
        """

        sota_tasks = []

        for task in TaskDb.tasks.values():
            find_sota_tasks(task, sota_tasks)

        return sota_tasks

    @staticmethod
    def datasets_with_sota() -> List[Dataset]:
        """
        Extract all datasets with SOTA tables.
        This includes both the top-level and subtasks

        :return:
        """

        sota_datasets = []

        for task in TaskDb.tasks.values():
            find_sota_datasets(task, sota_datasets)

        return sota_datasets


def find_sota_tasks(task:Task, out:List):
    """
    Get all the tasks with a SOTA table

    These tasks will be added into the "out" output list

    :param task:
    :param out:
    :return:
    """

    # check if the dataset has sota tables
    add = False
    for d in task.datasets:
        if d.sota_rows:
            add = True

        for sd in d.subdatasets:
            if sd.sota_rows:
                add = True

    if add:
        out.append(task)

    for subtask in task.subtasks:
        find_sota_tasks(subtask, out)


def find_sota_datasets(task:Task, out:List):
    """
    Get all the datasets with a SOTA table

    These datasets will be added into the "out" output list

    :param task:
    :param out:
    :return:
    """

    # check if the dataset has sota tables
    add = False
    for d in task.datasets:
        if d.sota_rows:
            out.append(d)

        for sd in d.subdatasets:
            if sd.sota_rows:
                out.append(sd)

    if add:
        out.append(task)

    for subtask in task.subtasks:
        find_sota_datasets(subtask, out)
