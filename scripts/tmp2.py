from elasticsearch import Elasticsearch
from rookie.utils import query_elasticsearch
from rookie.utils import query_results_to_bag_o_words
import collections

c = collections.Counter()

es = Elasticsearch()

results = query_elasticsearch("OPSB")

bag = query_results_to_bag_o_words(results)

print collections.Counter(bag).most_common(10)

'''
query = {"query": {"match": {"PERSON": "Johnson"}}}


res = es.search(index="lens", body=query)
print("Got %d Hits:" % res['hits']['total'])
for hit in res['hits']['hits']:
    print("%(headline)s" % hit["_source"])
#    print("%(entities)s" % hit["_source"])
'''
