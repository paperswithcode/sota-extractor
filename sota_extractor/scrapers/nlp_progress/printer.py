import textwrap
from typing import List

from sota_extractor.taskdb.v01 import Task, Dataset


def wrap_lines(value, indent=4) -> List[str]:
    prefix = " " * indent
    return [
        textwrap.indent(line, prefix=prefix) for line in textwrap.wrap(value)
    ]


def sub_items(title, items, lines_func) -> List[str]:
    lines = []
    if len(items) == 0:
        lines.append(f"{title}: -")
    else:
        lines.append(f"{title}:")
        for item in items:
            for i, line in enumerate(lines_func(item)):
                if i == 0:
                    lines.append(f"      - {line}")
                else:
                    lines.append(f"        {line}")
    return lines


def dataset_lines(dataset: Dataset) -> List[str]:
    lines = [f"Name: {dataset.name}"]
    if dataset.description is None or dataset.description.strip() == "":
        lines.append(f"Description: -")
    else:
        lines.append(f"Description:")
        lines.extend(wrap_lines(dataset.description))
    lines.append(f"Rows: {len(dataset.sota.rows)}")

    lines.extend(sub_items("Subdatasets", dataset.subdatasets, dataset_lines))
    return lines


def task_lines(task: Task) -> List[str]:
    lines = [f"Name: {task.name}"]
    if task.description is None or task.description.strip() == "":
        lines.append(f"Description: -")
    else:
        lines.append(f"Description:")
        lines.extend(wrap_lines(task.description))
    if task.parent is None:
        lines.append(f"Parent: -")
    else:
        lines.append(f"Parent: {task.parent.name}")
    if task.source_link is None:
        lines.append(f"Source Link: -")
    else:
        lines.append(f"Source Link: {task.source_link}")

    lines.extend(
        sub_items(
            title="Datasets", items=task.datasets, lines_func=dataset_lines
        )
    )

    lines.extend(
        sub_items(title="Subtasks", items=task.subtasks, lines_func=task_lines)
    )
    return lines


def print_task(task: Task):
    """Print a task.

    Used for debugging purposes.
    """
    lines = task_lines(task)
    print("\n".join(lines))
