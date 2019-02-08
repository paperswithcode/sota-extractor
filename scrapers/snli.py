import argparse
from scrapers.utils import get_soup
from extractor.taskdb import *

URL = "https://nlp.stanford.edu/projects/snli/"

parser = argparse.ArgumentParser()
parser.add_argument("--out", default="data/tasks/snli.json", help="Output JSON filename to use")
args = parser.parse_args()

out_filename = args.out

soup = get_soup(URL)

table = soup.findAll('table', attrs={'class': 'newstuff'})[1]

rows = table.findAll("tr")

sota_rows = []
suffix = ""
for row in rows:
    # ignore the header
    if row.get("class") == ["header"]:
        pass
    elif row.get("class") == ["section"]:
        suffix = row.text.replace("models", "").strip()
        continue
    else:
        cells = row.findAll("td")

        a = cells[0].find("a")

        paper_url = a.get("href")
        if paper_url == "http://nlp.stanford.edu/pubs/snli_paper.pdf":
            paper_title = "A large annotated corpus for learning natural language inference"
        elif paper_url == "https://www.nyu.edu/projects/bowman/spinn.pdf":
            paper_title = "A Fast Unified Model for Parsing and Sentence Understanding"
        else:
            paper_title = a.text

        model_name = cells[1].text.strip()
        if suffix:
            model_name = "%s (%s)" % (model_name, suffix)
        params = cells[2].text.strip()
        train_acc = cells[3].text.strip()
        test_acc = cells[4].text.strip()

        sota_rows.append(
            {
                "model_name": model_name,
                "paper_title": paper_title,
                "paper_url": paper_url,
                "metrics": {
                    "Test Accuracy": test_acc,
                    "Train Accuracy": train_acc,
                    "Parameters": params
                }
            }
        )

task = Task({
    "task": "Natural Language Inference",
    "datasets": [
        {
            "dataset": "SNLI",
            "sota": {
                "metrics": [
                    "Test Accuracy",
                    "Train Accuracy",
                    "Parameters"
                ],
                "rows": sota_rows
            }
        }
    ]
})

TaskDb.add_task("Natural Language Inference", task)
TaskDb.export_to_json(out_filename)



