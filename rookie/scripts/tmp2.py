from rookie.utils import query_elasticsearch
from elasticsearch import Elasticsearch
from rookie.classes import Result
es = Elasticsearch()

# result = query_elasticsearch("Gusman")

query = {"query": {"match": {"PERSON": "'Gov. Bobby Jindal'"}}}

res = es.search(index="lens",
                body=query,
                size=10000)

hits = res['hits']['hits']

print len(hits)

hits = [Result(r) for r in hits]

for h in hits:
    if "Gov. Bobby Jindal" in h.entities['PERSON']:
        print h.headline
