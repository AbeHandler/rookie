from elasticsearch import Elasticsearch

elasticsearch = Elasticsearch(sniff_on_start=True)

results = elasticsearch.search(index="lens", q="transportation OPSB", size=15)

print len(results['hits']['hits'])


#for hit in results['hits']['hits']:
#    print("%(timestamp)s %(headline)s %(links)s" % hit["_source"])