import sys
import argparse

from sota_extractor import serialization
from sota_extractor.scrapers.nlp_progress.printer import print_task
from sota_extractor.scrapers.nlp_progress.markdown import parse_file


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

    tdb = parse_file(ns.filename)

    if ns.json:
        print(serialization.dumps(tdb))
    else:
        for task in tdb.tasks.values():
            print_task(task)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
