from datetime import datetime
from elasticsearch import Elasticsearch

# by default we connect to localhost:9200
es = Elasticsearch()

# create an index in elasticsearch, ignore status code 400 (index already exists)
es.indices.create(index='my-index', ignore=400)

# datetimes will be serialized
es.index(index="my-index", doc_type="test-type", id=42, body={"any": "data", "timestamp": datetime.now()})
