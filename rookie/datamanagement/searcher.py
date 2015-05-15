#! /usr/bin/python

from elasticsearch import Elasticsearch

es = Elasticsearch(sniff_on_start=True)

# to do: add headline
res = es.search(index="lens", q = "OPSB")

print res