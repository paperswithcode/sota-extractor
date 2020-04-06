import io
import os
import re
import json
import glob
import logging
import argparse
from xml.etree.ElementTree import ElementTree
from typing import Dict, Tuple, List, Optional, Union
from dataclasses import dataclass, field, is_dataclass, asdict

import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions.tables import TableExtension


logger = logging.getLogger(__name__)


@dataclass
class Model:
    MODEL_NAME_RE = re.compile(
        r"""
        ^                              # Beginning
        \s*                            # Optional whitespace
        (?P<name>                      # Model name
            [^\(]+                     # Everything except open brace
        )?                             # Optional (can have only author)
        (?:                            # Optional author group
            \(                         # Open brace
                (?P<author>[^\)]+)     # Author
            \)                         # Closing brace
        )?                             # Optional
        \s*                            # Optional whitespace
        $                              # End
        """,
        re.VERBOSE | re.UNICODE,
    )

    name: Optional[str] = None
    author: Optional[str] = None

    @classmethod
    def parse(cls, s: str) -> Optional["Model"]:
        match = cls.MODEL_NAME_RE.match(s)
        if match is None:
            return None

        d = match.groupdict()
        name = d["name"]
        author = d["author"]
        if isinstance(name, str):
            name = name.strip()
        if isinstance(author, str):
            author = author.strip()
        return cls(name=name, author=author)


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except TypeError:
            if hasattr(o, "__json__"):
                return o.__json__()
            elif is_dataclass(o):
                return asdict(o)
            raise TypeError("%s is not JSON serializable" % o)


def dumps(obj, **kw):
    """Wrap `json.dumps` using the `JsonEncoder`."""
    return json.dumps(obj, cls=JsonEncoder, **kw)


@dataclass
class Link:
    title: str
    url: str

    @classmethod
    def nlp_progress(cls) -> "Link":
        return cls(
            title="NLP-progress",
            url="https://github.com/sebastianruder/NLP-progress",
        )


@dataclass
class Row:
    model_name: str
    metrics: Dict[str, str] = field(default_factory=dict)
    papert_title: str = ""
    paper_url: str = ""


@dataclass
class Sota:
    metrics: List[str] = field(default_factory=list)
    rows: List[Row] = field(default_factory=list)


@dataclass
class Dataset:
    name: str
    description: str = ""
    dataset_links: List[Link] = field(default_factory=list)
    subdatasets: List["Dataset"] = field(default_factory=list)
    sota: Optional[Sota] = None

    def __json__(self) -> dict:
        data = asdict(self)
        if len(self.dataset_links) == 0:
            del data["dataset_links"]
        if len(self.subdatasets) == 0:
            del data["subdatasets"]
        if self.sota is None:
            del data["sota"]
        return data


@dataclass
class Text:
    text: str = ""
    links: List[Link] = field(default_factory=list)

    @classmethod
    def _unwind(cls, el: ElementTree, keep_links) -> "Text":
        start = el.text or ""
        if el.tag == "a":
            links = [Link(title=el.text, url=el.attrib.get("href", None))]
        else:
            links = []

        children = ""
        for child in el:
            t = cls._unwind(child, keep_links=keep_links)
            children += t.text
            links.extend(t.links)

        end = el.tail or ""

        if el.tag == "a" and keep_links:
            return Text(
                text=f"[{start}]({el.attrib.get('href', '')}){children}{end}",
                links=links,
            )
        return Text(text=start + children + end, links=links)

    @classmethod
    def parse(
        cls, elements: Union[ElementTree, List[ElementTree]], keep_links=True
    ) -> "Text":
        if isinstance(elements, ElementTree):
            elements = [elements]
        text = cls()
        for el in elements:
            t = cls._unwind(el, keep_links=keep_links)
            text.text += t.text
            text.links.extend(t.links)
        return text


@dataclass
class Task:
    name: str
    description: str = ""
    subtasks: List["Task"] = field(default_factory=list)
    datasets: List[Dataset] = field(default_factory=list)
    source_link: Link = Link.nlp_progress()

    def __json__(self) -> dict:
        data = asdict(self)
        data["datasets"] = self.datasets
        return data


class ParserProcessor(Treeprocessor):
    def __init__(self, md=None):
        super().__init__(md=md)
        self.parsed = []

    @classmethod
    def _parse_sota(cls, table: ElementTree) -> Optional[Sota]:
        headers = [
            header.text.strip() for header in table.findall("thead/tr/th")
        ]
        headers_sanitized = [
            re.sub(r"\s+", "", header.lower()) for header in headers
        ]

        if "model" in headers_sanitized:
            model_idx = headers_sanitized.index("model")
        else:
            logger.error(
                "Model name not found in this SOTA table, skipping. "
                "Headers: %s",
                headers_sanitized,
            )
            return None

        if "paper/source" in headers_sanitized:
            paper_idx = headers_sanitized.index("paper/source")
        elif "paper" in headers_sanitized:
            paper_idx = headers.index("paper")
        else:
            logger.error(
                "Paper reference not found in this SOTA table, skipping. "
                "Headers: %s",
                headers_sanitized,
            )
            return None

        if "code" in headers_sanitized:
            code_idx = headers_sanitized.index("code")
        else:
            code_idx = None

        metrics_idx = sorted(
            set(range(len(headers))) - {model_idx, paper_idx, code_idx}
        )

        metrics_names = [headers[i] for i in metrics_idx]

        sota = Sota(metrics=metrics_names)

        for row in table.findall("tbody/tr"):
            cols = list(row)
            if len(cols) != len(headers):
                continue

            paper = Text.parse(cols[paper_idx], keep_links=False)
            model = Model.parse(cols[model_idx].text).name
            if model is None:
                continue
            sota.rows.append(
                Row(
                    model_name=model.name,
                    metrics={
                        name: cols[metrics_idx[i]].text.strip()
                        for i, name in enumerate(metrics_names)
                    },
                    papert_title=paper.text,
                    paper_url=(
                        paper.links[0].url if len(paper.links) > 0 else None
                    ),
                )
            )
        return sota

    @classmethod
    def _parse_subdatasets(
        cls, pairs: List[Tuple[ElementTree, ElementTree]]
    ) -> List[Dataset]:
        subdatasets = []
        for p, table in pairs:
            strong = p.find("strong")
            if strong is None:
                continue
            subdatasets.append(
                Dataset(
                    name=strong.text.strip().strip(":"),
                    sota=cls._parse_sota(table),
                )
            )
        return subdatasets

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

            # Task definition
            if header.tag == "h1":
                if task is not None:
                    self.parsed.append(task)

                task = Task(
                    name=header.text.strip(),
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
                    name=header.text.strip(),
                    description=Text.parse(
                        [e for e in section if e.tag == "p"]
                    ).text,
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
                        name=header.text.strip(),
                        description=text.text,
                        dataset_links=text.links,
                    )
                    if n_tables == 1:
                        dataset.sota = self._parse_sota(tables[0])
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
                        name=header.text.strip(),
                        description=text.text,
                        dataset_links=text.links,
                        subdatasets=self._parse_subdatasets(pairs),
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


def parse_markdown_file(md_file: str) -> List[Task]:
    """Parse a single markdown file.

    Args:
        md_file (str): Path to the markdown file.
    """

    md = Markdown()
    with io.open("/dev/null", "wb") as f:
        md.convertFile(md_file, output=f)
    return md.parser_processor.parsed


def parse_markdown_directory(path: str) -> List[Task]:
    """Parse all markdown files in a directory.

    Args:
        path (str): Path to the directory
    """
    md_files = glob.glob(os.path.join(path, "*.md"))

    result = []
    for md_file in md_files:
        logger.info("Processing `%s`...", md_file)
        result.extend(parse_markdown_file(md_file))

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "paths", nargs="+", type=str, help="Files or directories to convert"
    )
    parser.add_argument(
        "--output",
        default="structured.json",
        type=str,
        help="Output JSON file name",
    )

    args = parser.parse_args()

    out = []
    for path in [os.path.abspath(p) for p in args.paths]:
        if os.path.isdir(path):
            out.extend(parse_markdown_directory(path))
        else:
            out.extend(parse_markdown_file(path))

    with io.open(args.output, "w") as f:
        f.write(dumps(out, indent=2))
