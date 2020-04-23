import io
import logging
from typing import List

import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions.tables import TableExtension

from sota_extractor.taskdb.v01 import Task, Dataset, TaskDB
from sota_extractor.scrapers.nlp_progress.fixer import fix_task
from sota_extractor.scrapers.nlp_progress.parsers import (
    Text,
    parse_sota,
    parse_subdatasets,
)


logger = logging.getLogger(__name__)


class ParserProcessor(Treeprocessor):
    def __init__(self, md=None):
        super().__init__(md=md)
        self.parsed: List[Task] = []

    def run(self, root):
        # Assumptions:
        # 1) H1 are tasks
        # 2) Everything until the next heading is the task description
        # 3) H2 are subtasks, H3 are datasets, H4 are subdatasets

        # Algorithm:
        # 1) Split the document by headings
        sections = []
        cur = []
        for el in root:
            if el.tag in {"h1", "h2", "h3", "h4", "h5"}:
                if cur:
                    sections.append(cur)
                    cur = [el]
                else:
                    cur = [el]
            else:
                cur.append(el)

        if cur:
            sections.append(cur)

        # 2) Parse each heading section one-by-one
        task = None  # current task element being parsed
        subtask = None  # current subtask being parsed
        dataset = None  # current dataset being parsed

        for section_index in range(len(sections)):
            section = sections[section_index]
            header = section[0]

            if header.text is None:
                # Invalid section
                continue

            # Task definition
            if header.tag == "h1":
                if task is not None:
                    self.parsed.append(task)

                task = Task(
                    name=header.text.strip().title(),
                    description=Text.parse(
                        [e for e in section if e.tag == "p"]
                    ).text,
                )

                # reset subtasks and datasets
                subtask = None
                dataset = None

            # Subtask definition
            if header.tag == "h2":
                if task is None:
                    logger.error(
                        "Unexpected subtask without a parent task at: %s",
                        header.text,
                    )

                # new substask
                subtask = Task(
                    name=header.text.strip().title(),
                    description=Text.parse(
                        [e for e in section if e.tag == "p"]
                    ).text,
                    parent=task,
                )
                task.subtasks.append(subtask)

                # reset the last dataset
                dataset = None

            # Dataset definition
            if header.tag == "h3" and "Table of content" not in header.text:
                if task is None:
                    logger.error(
                        "Unexpected dataset without a parent task at: %s",
                        header.text,
                    )

                tables = [t for t in section if t.tag == "table"]
                n_tables = len(tables)
                if n_tables < 2:
                    text = Text.parse([e for e in section if e.tag == "p"])
                    dataset = Dataset(
                        name=header.text.strip().strip(":"),
                        description=text.text,
                        links=text.links,
                    )
                    if n_tables == 1:
                        dataset.sota = parse_sota(tables[0])
                else:
                    table_idxs = [
                        i for i, el in enumerate(section) if el.tag == "table"
                    ]
                    pairs = []
                    for idx in table_idxs:
                        if idx >= 2 and section[idx - 1].tag == "p":
                            pairs.append((section[idx - 1], section[idx]))

                    description_idxs = set(range(1, len(section))) - set(
                        table_idxs
                    )
                    description_ps = [
                        el
                        for i, el in enumerate(section)
                        if i in description_idxs
                    ]
                    text = Text.parse(description_ps)
                    dataset = Dataset(
                        name=header.text.strip().strip(":"),
                        description=text.text,
                        links=text.links,
                    )
                    dataset.subdatasets = parse_subdatasets(
                        parent=dataset, pairs=pairs
                    )

                if subtask is not None:
                    # we are in a subtask, add everything here
                    subtask.datasets.append(dataset)
                else:
                    task.datasets.append(dataset)

        if task:
            self.parsed.append(task)


class Markdown(markdown.Markdown):
    def __init__(self):
        super().__init__(extensions=[TableExtension()])
        self.parser_processor = ParserProcessor(self)
        self.treeprocessors.register(
            self.parser_processor, "parser_processor", 1
        )


def parse_file(filename: str) -> TaskDB:
    """Parse an NLP-Progress markdown file and return a TaskDB instance."""
    md = Markdown()
    with io.open("/dev/null", "wb") as f:
        md.convertFile(filename, output=f)

    tdb = TaskDB()
    for task in md.parser_processor.parsed:
        for t in fix_task(task):
            tdb.add_task(t)
    return tdb
