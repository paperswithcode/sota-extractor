import re
import gzip


from extractor.taskdb import *
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.porter import PorterStemmer

# load the tasks and arxiv metadata

stemmer = PorterStemmer()

TaskDb.load_tasks(["data/tasks/nlpprogress.json"])
TaskDb.load_synonyms(["data/tasks/synonyms.csv"])
with gzip.open("data/arxiv_aclweb.json.gz") as f:
    arxiv = json.load(f)

for a in arxiv:
    if a["abstract"] is None:
        a["abstract"] = ""

# require and normalise arxiv titles
arxiv = [a for a in arxiv if "title" in a and a["title"] is not None]
for a in arxiv:
    a["title"] = re.sub(" +", " ", a["title"].replace("\n", " "))
    a["title_lower"] = a["title"].lower()
    a["abstract_lower"] = a["abstract"].lower()
    a["title_stem"] = stemmer.stem(a["title"])
    a["abstract_stem"] = stemmer.stem(a["abstract"])
