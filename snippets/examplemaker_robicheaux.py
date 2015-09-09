
import pdb
from experiment.cloud_searcher import query_cloud_search
from experiment.cloud_searcher import get_representitive_item
import itertools
from collections import defaultdict
import collections
import pickle

from experiment.simplemerger import Merger

q = "Orleans Parish Prison"
term = "vera institute"

results = [r for r in query_cloud_search(q)]

has_term = []

for r in results:
    if term in r['fields']['text'].lower():
        has_term.append(r)

for result in has_term:
    print result['fields']['url']
