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

    t = task.task.lower()
    ts = stemmer.stem(task.task)
    title = paper["title_lower"]
    abstract = paper["abstract_lower"]
    title_stem = paper["title_stem"]
    abstract_stem = paper["abstract_stem"]

    matches_paper = t in title or t in abstract or ts in title_stem or ts in abstract_stem

    contains_sota = "state-of-the-art" in abstract or "state-of-art" in abstract or \
        "state of the art" in abstract or "state of art" in abstract or "sota" in abstract

    return matches_paper and contains_sota

