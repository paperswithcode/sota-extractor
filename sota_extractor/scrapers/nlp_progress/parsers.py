import re
import logging
from xml.etree.ElementTree import ElementTree
from typing import Optional, List, Union, Tuple

from sota_extractor.taskdb.v01 import Sota, SotaRow, Dataset, Link


logger = logging.getLogger(__name__)


def nlp_progress_link() -> Link:
    return Link(
        title="NLP-progress",
        url="https://github.com/sebastianruder/NLP-progress",
    )


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

    def __init__(
        self, name: Optional[str] = None, author: Optional[str] = None
    ):
        self.name = name
        self.author = author

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


class Text:
    def __init__(self, text: str = "", links: List[Link] = None):
        self.text = text
        self.links = links or []

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
            return cls(
                text=f"[{start}]({el.attrib.get('href', '')}){children}{end}",
                links=links,
            )
        return cls(text=start + children + end, links=links)

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


def parse_sota(table: ElementTree) -> Optional[Sota]:
    headers = [
        (header.text or "").strip() for header in table.findall("thead/tr/th")
    ]
    headers_sanitized = [
        re.sub(r"\s+", "", header.lower()) for header in headers
    ]

    if "model" in headers_sanitized:
        model_idx = headers_sanitized.index("model")
    else:
        logger.error(
            "Model name not found in this SOTA table, skipping. Headers: %s",
            headers_sanitized,
        )
        return None

    if "paper/source" in headers_sanitized:
        paper_idx = headers_sanitized.index("paper/source")
    elif "paper" in headers_sanitized:
        paper_idx = headers_sanitized.index("paper")
    else:
        logger.error(
            "Paper not found in this SOTA table, skipping. Headers: %s",
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
            # Skip row not enough columns.
            continue

        paper = Text.parse(cols[paper_idx], keep_links=False)
        model = Model.parse(cols[model_idx].text)
        if model is None:
            # Skip row model cannot be determined.
            continue

        sota.rows.append(
            SotaRow(
                model_name=model.name,
                paper_title=paper.text,
                paper_url=paper.links[0].url if len(paper.links) > 0 else "",
                metrics={
                    name: (cols[metrics_idx[i]].text or "").strip()
                    for i, name in enumerate(metrics_names)
                },
            )
        )
    return sota


def parse_subdatasets(
    parent: Dataset, pairs: List[Tuple[ElementTree, ElementTree]]
) -> List[Dataset]:
    subdatasets = []
    for p, table in pairs:
        strong = p.find("strong")
        if strong is None:
            continue
        subdatasets.append(
            Dataset(
                name=strong.text.strip().strip(":"),
                is_subdataset=True,
                parent=parent,
                sota=parse_sota(table),
            )
        )
    return subdatasets
