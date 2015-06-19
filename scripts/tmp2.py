from rookie.utils import query_elasticsearch

result = query_elasticsearch("Gusman")

print result.trigrams

# query = {"query": {"match": {"PERSON": results.persons[0].name}}}

# res = es.search(index="lens",
#                body=query,
#                size=10000)

# hits = res['hits']['hits']

# hits = [Result(r) for r in hits]

# for h in hits:
#    print h
