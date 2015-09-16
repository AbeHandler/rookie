
import pdb
import glob
from experiment.cloud_searcher import query_cloud_search
from experiment.cloud_searcher import get_representitive_item
from experiment.cloud_searcher import get_overview
import itertools
from rookie.classes import IncomingFile
from collections import defaultdict
import collections
import pickle

from itertools import tee, izip, islice, chain


def pairwise(iterable, n=2):
    return izip(*(islice(it, pos, None) for pos, it in enumerate(tee(iterable, n))))

def get_ngrams(words, n=2):
    stopwords = [i.replace("\n", "") for i in open("stopwords.txt")]
    words = [i for i in words if i not in stopwords]
    return pairwise(words, n)

processed_location = "/Users/ahandler/research/rookie/data/lens_processed"

files_to_check = glob.glob(processed_location + "/*")

q = "coastal restoration"

results = [r for r in query_cloud_search(q)]

all_text = ""
filtered = []


for r in results:
    all_text = all_text + r['fields']['text'].lower()
    try:
        filtered.append(r['fields']['ngrams'])
    except KeyError:
        pass

total_filteredngrms = []

for nset in filtered:
    for gram in nset:
        total_filteredngrms.append(gram)

twograms = set([o for o in get_ngrams(all_text.split(" "))])
threegrams = set([o for o in get_ngrams(all_text.split(" ") ,3)])
fourgrams = set([o for o in get_ngrams(all_text.split(" ") , 4)])
print len(twograms) + len(threegrams) + len(fourgrams)
pdb.set_trace()