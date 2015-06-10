"""
Quickie debugging
"""

from elasticsearch import Elasticsearch
from rookie.utils import query_elasticsearch
from rookie.utils import get_node_degrees


def search(q):

    results = query_elasticsearch(q)

    node_degrees = get_node_degrees(results)

    for result in results:
        result.link_degree = node_degrees[result.docid]

    return results

results = search("headline=Other charters will get material from closed Lagniappe Academies")

for r in results:
    print r.headline