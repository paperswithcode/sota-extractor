import re
import gzip
from extractor.taskdb import *
from nltk.stem.snowball import SnowballStemmer

# load the tasks and arxiv metadata

stemmer = SnowballStemmer("english")

TaskDb.load_tasks(["data/tasks/nlpprogress.json"])
with gzip.open("data/arxiv_metadata.json.gz") as f:
    arxiv = json.load(f)

# require and normalise arxiv titles
arxiv = [a for a in arxiv if "title" in a and a["title"] is not None]
for a in arxiv:
    a["title"] = re.sub(" +", " ", a["title"].replace("\n", " "))
    a["title_lower"] = a["title"].lower()
    a["abstract_lower"] = a["abstract"].lower()
    a["title_stem"] = stemmer.stem(a["title"])
    a["abstract_stem"] = stemmer.stem(a["abstract"])
