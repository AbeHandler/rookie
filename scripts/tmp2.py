from elasticsearch import Elasticsearch
from rookie.utils import query_elasticsearch
from rookie.utils import query_results_to_bag_o_words
from rookie.utils import query_results_to_bag_o_entities

import collections

c = collections.Counter()

es = Elasticsearch()

results = query_elasticsearch("OPSB")

entities = query_results_to_bag_o_entities(results)

print collections.Counter(entities['PERSON']).most_common(25)

bag = query_results_to_bag_o_words(results)

#print collections.Counter(bag).most_common(10)

'''
query = {"query": {"match": {"PERSON": "Johnson"}}}


res = es.search(index="lens", body=query)
print("Got %d Hits:" % res['hits']['total'])
for hit in res['hits']['hits']:
    print("%(headline)s" % hit["_source"])
#    print("%(entities)s" % hit["_source"])
'''
