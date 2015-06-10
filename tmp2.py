from elasticsearch import Elasticsearch
es = Elasticsearch()

# query = {"query": {"match_all": {}}, "filter": {"exists" : { "field" : "PERSON" }}}

# query = {"filter": {"term": {"PERSON": "johnson"}}}

query = { "query" : { "match" : { "PERSON" : "Johnson"}} }


res = es.search(index="lens", body=query)
print("Got %d Hits:" % res['hits']['total'])
for hit in res['hits']['hits']:
    print("%(headline)s" % hit["_source"])
#    print("%(entities)s" % hit["_source"])