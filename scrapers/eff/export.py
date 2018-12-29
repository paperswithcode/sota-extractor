import json
from typing import Dict

from data.acoustics import *
from data.awty import *
from data.generative import *
from data.language import *
from data.stem import *
from data.strategy_games import *
from data.video_games import *
from data.vision import *
from data.wer import *

all_problems = [
    speech_recognition,
    instrumentals_recognition,
    image_generation,
    scene_generation,
    modelling_english,
    turing_test,
    easy_turing_test,
    reading_comprehension,
    translation,
    read_stem_papers,
    extract_results,
    solve_technical_problems,
    program_induction,
    vaguely_constrained_technical_problems,
    solve_constrained_technical_problems,
    theorem_proving,
    circuit_design,
    program_induction,
    understand_conditional_expressions,
    science_question_answering,
    abstract_strategy_games,
    playing_with_hints,
    mastering_historical_games,
    learning_abstract_game_rules,
    learning_arbitrary_abstract_games,
    computer_games,
    games_requiring_novel_language,
    games_requiring_speech,
    games_requiring_language_comprehension,
    simple_games,
    vision,
    image_comprehension,
    image_classification,
    video_classification,
]

def extract_problems_with_metrics(problem, out):
    """
    Extract problems with metrics and put them into the `out` list

    :param problem: a Problem object
    :param out:
    :return:
    """
    if problem.metrics:
        out.append(problem)

    for subproblem in problem.subproblems:
        extract_problems_with_metrics(subproblem, out)


# output list
out = []

# Extract all problems that have metrics attached to them
for problem in all_problems:
    prob_metrics = []

    extract_problems_with_metrics(problem, prob_metrics)

    for p in prob_metrics:
        task = {
            "task": p.name,
            "description": "",
            "categories": p.attributes,
        }

        datasets = []
        for m in p.metrics:
            dataset = {
                "dataset": m.name,
                "description": m.notes,
                "dataset_links": [
                    {
                        "title": m.name,
                        "url": m.data_url
                    }
                ]
            }

            sota = {
                "metrics": [m.axis_label],
            }

            sota_rows = []
            for mm in m.measures:
                row = {
                    "model_name": mm.name,
                    "paper_title": mm.papername,
                    "paper_url": mm.url,
                    "metrics": {
                    }
                }
                row["metrics"][m.axis_label] = mm.value
                sota_rows.append(row)

            sota["rows"] = sota_rows
            dataset["sota"] = sota

            datasets.append(dataset)

        task["datasets"] = datasets

        out.append(task)

print("Deduplicating the lists...")
json_list = [json.dumps(d, indent=2) for d in out]
json_list = list(set(json_list))

out_dedup = [json.loads(s) for s in json_list]

row_count = 0
for t in out_dedup:
    for d in t["datasets"]:
        row_count += len(d["sota"]["rows"])

print("Got %d tasks, %d rows" % (len(out_dedup), row_count))
[print("Task: %s %s" % (t["task"], t["categories"])) for t in out_dedup ]

with open("export.json", "w") as f:
    f.write(json.dumps(out_dedup, indent=2))