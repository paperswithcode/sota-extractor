from datetime import datetime
from sota_extractor.errors import DataError
from sota_extractor.scrapers.utils import get_soup
from sota_extractor.taskdb.v01 import SotaRow, Dataset, Task, Link, TaskDB

SQUAD_URL = "https://rajpurkar.github.io/SQuAD-explorer/"


TASK_NAME = "Question Answering"
DATASET_1_NAME = "SQuAD1.1"
DATASET_1_DESCRIPTION = (
    "Previous version of the SQuAD2.0 dataset with 50,000 question-answer "
    "pairs."
)
DATASET_2_NAME = "SQuAD2.0"
DATASET_2_DESCRIPTION = (
    "Stanford Question Answering Dataset (SQuAD) is a reading comprehension "
    "dataset, consisting of questions posed by crowdworkers on a set of "
    "Wikipedia articles, where the answer to every question is a segment of "
    "text, or span, from the corresponding reading passage, or the question "
    "might be unanswerable."
)


def get_sota_rows(table):
    rows = table.findAll("tr")

    sota_rows = []
    for row in rows:
        klass = row.attrs.get("class")
        if klass and klass[0] == "human-row":
            # Skip the human performance row
            continue
        cells = row.findAll("td")
        if len(cells) == 4:
            date_span = cells[0].select_one("span.date")
            if date_span is not None:
                date = datetime.strptime(date_span.text, "%b %d, %Y")
            else:
                date = None
            model = cells[1]
            m_em = cells[2].text
            m_f1 = cells[3].text

            if model.find("a"):
                sota_rows.append(
                    SotaRow(
                        model_name=model.find(text=True, recursive=False),
                        paper_title=model.find("a").text,
                        paper_url=model.find("a")["href"],
                        paper_date=date,
                        metrics={"EM": m_em, "F1": m_f1},
                    )
                )
            else:
                sota_rows.append(
                    SotaRow(
                        model_name=model.find(text=True, recursive=False),
                        paper_date=date,
                        metrics={"EM": m_em, "F1": m_f1},
                    )
                )

    return sota_rows


def squad():
    """Extract SQUAD SOTA tables."""
    soup = get_soup(SQUAD_URL)

    sota_tabels = soup.findAll("table", attrs={"class": "performanceTable"})

    if len(sota_tabels) == 2:
        squad2 = sota_tabels[0]
        squad1 = sota_tabels[1]

        dataset2 = Dataset(
            name=DATASET_2_NAME,
            is_subdataset=False,
            description=DATASET_2_DESCRIPTION,
        )
        dataset1 = Dataset(
            name=DATASET_1_NAME,
            is_subdataset=False,
            description=DATASET_1_DESCRIPTION,
        )

        task = Task(name="Question Answering")
        task.datasets = [dataset2, dataset1]
        task.source_link = Link(title="SQuAD Leaderboard", url=SQUAD_URL)

        # scrape the evaluation values on the two datasets
        dataset2.sota.metrics = ["EM", "F1"]
        dataset1.sota.metrics = ["EM", "F1"]

        dataset2.sota.rows = get_sota_rows(squad2)
        dataset1.sota.rows = get_sota_rows(squad1)

        tdb = TaskDB()
        tdb.add_task(task)
        return tdb.export()
    else:
        raise DataError("Got an unexpected number of SOTA tables.")
