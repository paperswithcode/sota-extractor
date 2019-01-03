import argparse
from scrapers.utils import get_soup
from extractor.taskdb import *

URL = "https://rajpurkar.github.io/SQuAD-explorer/"

def get_sota_rows(table):
    rows = table.findAll("tr")

    sota_rows = []
    for row in rows:
        cells = row.findAll("td")
        if len(cells) == 4:
            model = cells[1]
            m_em = cells[2].text
            m_f1 = cells[3].text

            if model.find("a"):
                sota_rows.append(SotaRow({
                    "model_name": model.find(text=True, recursive=False),
                    "paper_title": model.find("a").text,
                    "paper_url": model.find("a")["href"],
                    "metrics": {
                        "EM": m_em,
                        "F1": m_f1,
                    }
                }))
            else:
                sota_rows.append(SotaRow({
                    "model_name": model.find(text=True, recursive=False),
                    "metrics": {
                        "EM": m_em,
                        "F1": m_f1,
                    }
                }))

    return sota_rows


parser = argparse.ArgumentParser()
parser.add_argument("--out", default="data/tasks/squad.json", help="Output JSON filename to use")
args = parser.parse_args()

out_filename = args.out

soup = get_soup(URL)

sota_tabels = soup.findAll('table', attrs={'class': 'performanceTable'})

if len(sota_tabels) == 2:
    squad2 = sota_tabels[0]
    squad1 = sota_tabels[1]

    dataset2 = Dataset({"dataset": "SQuAD2.0", "description": "Stanford Question Answering Dataset (SQuAD) is a reading comprehension dataset, consisting of questions posed by crowdworkers on a set of Wikipedia articles, where the answer to every question is a segment of text, or span, from the corresponding reading passage, or the question might be unanswerable."})
    dataset1 = Dataset({"dataset": "SQuAD1.1", "description": "Previous version of the SQuAD2.0 dataset with 50,000 question-answer pairs."})

    task = Task({"task": "Question answering"})
    task.datasets = [dataset2, dataset1]
    task.source_link = Link({"title": "SQuAD Leaderboard", "url": URL})

    # scrape the evaluation values on the two datasets
    dataset2.sota_metrics = ["EM", "F1"]
    dataset1.sota_metrics = ["EM", "F1"]

    dataset2.sota_rows = get_sota_rows(squad2)
    dataset1.sota_rows = get_sota_rows(squad1)

    TaskDb.add_task("qa", task)
    TaskDb.export_to_json(out_filename)

else:
    print("ERROR: got an unexpected number of SOTA tables")

