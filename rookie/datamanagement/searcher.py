from elasticsearch import Elasticsearch
import networkx as nx

G = nx.Graph()


def add_node(nid, headline):
    if nid in G.nodes():
        G.add_node(int(nid), headline=headline)


elasticsearch = Elasticsearch(sniff_on_start=True)

results = elasticsearch.search(index="lens", q="OPSB", size=150000)

for result in results['hits']['hits']:
    headline = result['_source']['headline']
    add_node(result['_id'], headline)
    for link in result['_source']['links']:
        G.add_edge(int(result['_id']), link[1])

node_degress = []

for node in G.nodes():
    node_degress.append((node, nx.degree(G, node)))

nodes = sorted(node_degress, key=lambda node: node[1], reverse=True)

for node in nodes:
    print node

# print len(results['hits']['hits'])

# for hit in results['hits']['hits']:
#    print hit.keys()
#    print("%(timestamp)s %(id)s %(links)s" % hit["_source"])