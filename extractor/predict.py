import pprint
from extractor.taskdb import *
from extractor.load import TaskDb, arxiv, stemmer

def article_matches(paper:Dict, task:Task, stemmer):
    """
    See if a paper mentions the tasks

    By mentioning it in the title or abstract
    And also mentioning state-of-the-art

    :param paper:
    :param task:
    :param stemmer:
    :return:
    """

    title = paper["title_lower"]
    abstract = paper["abstract_lower"]
    title_stem = paper["title_stem"]
    abstract_stem = paper["abstract_stem"]

    all_task_names = [task.task]
    all_task_names.extend(task.synonyms)

    matches_paper = False
    for task_name in all_task_names:
        task_name_lower = task_name.lower()
        task_name_stem = stemmer.stem(task_name)

        matches_paper = matches_paper or task_name_lower in title
        matches_paper = matches_paper or task_name_lower in abstract
        #matches_paper = matches_paper or task_name_stem in title_stem
        #matches_paper = matches_paper or task_name_stem in abstract_stem

    contains_sota = "state-of-the-art" in abstract or "state-of-art" in abstract or \
        "state of the art" in abstract or "state of art" in abstract or "sota" in abstract

    return matches_paper and contains_sota

