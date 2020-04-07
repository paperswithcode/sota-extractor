from sota_extractor.errors import DataError
from sota_extractor.scrapers.utils import get_soup
from sota_extractor.taskdb.v01 import SotaRow, Dataset, Task, Link, TaskDB

CITYSCAPES_URL = (
    "https://www.cityscapes-dataset.com/benchmarks/#pixel-level-results"
)


TASK_NAME = "Semantic Segmentation"
DATASET_NAME = "Cityscapes test"
DATASET_DESCRIPTION = (
    "The first Cityscapes task involves predicting a per-pixel semantic "
    "labeling of the image without considering higher-level object instance "
    "or boundary information."
)


def get_sota_rows(table):
    rows = table.findAll("tr")

    sota_rows = []
    for row in rows:
        if row.find("th"):
            # Skip the header row
            continue
        cells = row.findAll("td")
        if len(cells) == 24:
            model_name = row.find("td", attrs={"class": "column-1"}).text
            paper_title = row.find("td", attrs={"class": "column-21"}).text
            if row.find("td", attrs={"class": "column-21"}).a:
                paper_url = row.find("td", attrs={"class": "column-21"}).a[
                    "href"
                ]
            else:
                paper_url = None
            class_iou = row.find("td", attrs={"class": "column-14"}).text
            category_iou = row.find("td", attrs={"class": "column-16"}).text

            if paper_title and class_iou and category_iou:
                sota_row = SotaRow(
                    model_name=model_name,
                    paper_title=paper_title,
                    paper_url=paper_url,
                    paper_date=None,
                    metrics={
                        "Mean IoU (class)": class_iou,
                        "Mean IoU (category)": category_iou,
                    },
                )
                sota_rows.append(sota_row)

    return sota_rows


def cityscapes() -> TaskDB:
    """Extract Cityscapes SOTA tables."""
    soup = get_soup(CITYSCAPES_URL)

    sota_tabels = soup.findAll("table", attrs={"class": "tablepress"})

    if len(sota_tabels) == 3:

        cityscapes = sota_tabels[0]  # pixel-level semantic segmentation task

        dataset = Dataset(
            name=DATASET_NAME,
            is_subdataset=False,
            description=DATASET_DESCRIPTION,
        )

        task = Task(name="Semantic Segmentation")
        task.datasets = [dataset]
        task.source_link = Link(
            title="CityScapes Leaderboard", url=CITYSCAPES_URL
        )

        # scrape the evaluation values on the two datasets
        dataset.sota.metrics = ["Mean IoU (class)", "Mean IoU (class)"]

        dataset.sota.rows = get_sota_rows(cityscapes)

        tdb = TaskDB()
        tdb.add_task(task)
        return tdb
    else:
        raise DataError("Got an unexpected number of SOTA tables.")
