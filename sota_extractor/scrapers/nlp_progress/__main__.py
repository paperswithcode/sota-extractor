import io
import sys
import argparse

from sota_extractor import serialization
from sota_extractor.taskdb.v01 import TaskDB
from sota_extractor.scrapers.nlp_progress.fixer import fix_task
from sota_extractor.scrapers.nlp_progress.markdown import Markdown
from sota_extractor.scrapers.nlp_progress.printer import print_task


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        default=False,
        help="Print the taskdb json output.",
    )
    ns = parser.parse_args(args)

    md = Markdown()
    with io.open("/dev/null", "wb") as f:
        md.convertFile(ns.filename, output=f)

    tdb = TaskDB()
    for task in md.parser_processor.parsed:
        task = fix_task(task)
        if task is not None:
            tdb.add_task(task)

    if ns.json:
        print(serialization.dumps(tdb))
    else:
        for task in tdb.tasks.values():
            print_task(task)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
