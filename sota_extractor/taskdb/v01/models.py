from typing import List, Optional, Dict
from dataclasses import dataclass, field


@dataclass
class Link:
    title: str = ""
    url: str = ""


@dataclass
class SotaRow:
    model_name: str
    paper_title: str = ""
    paper_url: str = ""
    paper_date: Optional[str] = None
    code_links: List[Link] = field(default_factory=list)
    model_links: List[Link] = field(default_factory=list)
    metrics: Dict[str, str] = field(default_factory=dict)
    uses_additional_data: bool = False


@dataclass
class Sota:
    metrics: List[str] = field(default_factory=list)
    rows: List[SotaRow] = field(default_factory=list)


@dataclass
class Dataset:
    name: str
    is_subdataset: bool = False
    description: str = ""
    parent: "Dataset" = None
    sota: Sota = field(default_factory=lambda: Sota())
    subdatasets: List["Dataset"] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)
    citations: List[Link] = field(default_factory=list)


@dataclass
class Task:
    name: str
    description: str = ""
    parent: "Task" = None
    categories: List[str] = field(default_factory=list)
    datasets: List[Dataset] = field(default_factory=list)
    subtasks: List["Task"] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    source_link: Link = None
