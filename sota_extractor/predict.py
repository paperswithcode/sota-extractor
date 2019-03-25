from typing import Dict
from sota_extractor.taskdb import Task


def article_matches(paper: Dict, task: Task):
    """Check if a paper mentions the tasks.

    By mentioning it in the title or abstract.
    And also mentioning state-of-the-art.
    """

    title = paper["title_lower"]
    abstract = paper["abstract_lower"]

    all_task_names = [task.task]
    all_task_names.extend(task.synonyms)

    matches_paper = False
    for task_name in all_task_names:
        task_name_lower = task_name.lower()
        matches_paper = matches_paper or task_name_lower in title
        matches_paper = matches_paper or task_name_lower in abstract

    contains_sota = (
        "state-of-the-art" in abstract
        or "state-of-art" in abstract
        or "state of the art" in abstract
        or "state of art" in abstract
        or "sota" in abstract
    )

    return matches_paper and contains_sota
