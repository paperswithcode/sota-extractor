import os
import glob
import logging
import tempfile
import subprocess

from sota_extractor.errors import DataError
from sota_extractor.taskdb.v01 import TaskDB
from sota_extractor.consts import NLP_PROGRESS_REPO
from sota_extractor.scrapers.nlp_progress.markdown import parse_file

logger = logging.getLogger(__name__)


def nlp_progress() -> TaskDB:
    """Parse a the whole nlp progress repo or a single markdown file.

    Checkouts the nlp progress git repository and parses all the markdown files
    in it.

    Returns:
        TaskDB: Populated task database.
    """
    tdb = TaskDB()

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = os.path.join(tmpdir, "nlp-progress")
        cp = subprocess.run(
            ["git", "clone", NLP_PROGRESS_REPO, repo_path], capture_output=True
        )
        if cp.returncode != 0:
            logger.error("stdout: %s", cp.stdout)
            logger.error("stderr: %s", cp.stderr)
            raise DataError("Could not clone the NLP Progress repository.")

        filenames = glob.glob(os.path.join(repo_path, "english", "*.md"))

        for filename in filenames:
            file_tdb = parse_file(filename)
            for task in file_tdb.tasks.values():
                tdb.add_task(task)

    return tdb
