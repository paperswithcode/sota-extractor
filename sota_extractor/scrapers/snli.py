from sota_extractor.scrapers.utils import get_soup
from sota_extractor.taskdb.v01 import (
    Link,
    Task,
    Dataset,
    Sota,
    SotaRow,
    TaskDB,
)

SNLI_URL = "https://nlp.stanford.edu/projects/snli/"


def snli() -> TaskDB:
    """Extract SNLI SOTA tables."""
    soup = get_soup(SNLI_URL)

    table = soup.findAll("table", attrs={"class": "newstuff"})[1]

    rows = table.findAll("tr")

    sota_rows = []
    # suffix = ""
    for row in rows:
        # ignore the header
        if row.get("class") == ["header"]:
            pass
        elif row.get("class") == ["section"]:
            # suffix = row.text.replace("models", "").strip()
            continue
        else:
            cells = row.findAll("td")

            a = cells[0].find("a")

            paper_url = a.get("href")
            if paper_url == "http://nlp.stanford.edu/pubs/snli_paper.pdf":
                paper_title = (
                    "A large annotated corpus for learning natural language "
                    "inference"
                )
            elif paper_url == "https://www.nyu.edu/projects/bowman/spinn.pdf":
                paper_title = (
                    "A Fast Unified Model for Parsing and Sentence "
                    "Understanding"
                )
            elif (
                paper_url
                == "https://s3-us-west-2.amazonaws.com/openai-assets/"
                "research-covers/language-unsupervised/"
                "language_understanding_paper.pdf"
            ):
                paper_title = (
                    "Improving Language Understanding by Generative "
                    "Pre-Training"
                )
            elif (
                paper_url == "https://pdfs.semanticscholar.org/adc1/"
                "84fcb04107f95e35ea1b07ef9aad749da8d7.pdf"
            ):
                paper_title = "Deep Fusion LSTMs for Text Semantic Matching"
            else:
                paper_title = a.text

            model_name = cells[1].text.strip()
            # if suffix:
            #    model_name = "%s (%s)" % (model_name, suffix)

            model_name = model_name.replace("(code)", "").strip()

            params = cells[2].text.strip()
            train_acc = cells[3].text.strip()
            test_acc = cells[4].text.strip()

            sota_rows.append(
                SotaRow(
                    model_name=model_name,
                    paper_title=paper_title,
                    paper_url=paper_url,
                    metrics={
                        "% Test Accuracy": test_acc,
                        "% Train Accuracy": train_acc,
                        "Parameters": params,
                    },
                )
            )

    task = Task(
        name="Natural Language Inference",
        datasets=[
            Dataset(
                name="SNLI",
                is_subdataset=False,
                sota=Sota(
                    metrics=[
                        "% Test Accuracy",
                        "% Train Accuracy",
                        "Parameters",
                    ],
                    rows=sota_rows,
                ),
            )
        ],
        source_link=Link(
            title="The Stanford Natural Language Inference (SNLI) Corpus",
            url="https://nlp.stanford.edu/projects/snli/",
        ),
    )
    tdb = TaskDB()
    tdb.add_task(task)
    return tdb
