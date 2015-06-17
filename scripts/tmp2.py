from elasticsearch import Elasticsearch
from rookie.utils import query_elasticsearch
from rookie.classes import Result

import collections

c = collections.Counter()

results = query_elasticsearch("Gusman")

for p in results.persons:
    print p.timestamps

# query = {"query": {"match": {"PERSON": results.persons[0].name}}}

# res = es.search(index="lens",
#                body=query,
#                size=10000)

# hits = res['hits']['hits']

# hits = [Result(r) for r in hits]

# for h in hits:
#    print h
