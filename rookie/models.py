"""
The web app that runs at vault.thelensnola.org/contracts.
"""

from rookie import (
    log
)

from elasticsearch import Elasticsearch
import networkx as nx


def add_node(G, nid, headline):
    if nid not in G.nodes():
        doc, sentence = nid.split("-")
        G.add_node(int(doc), headline=headline)


class Models(object):

    '''doctstring'''

    def __init__(self):
        '''docstring'''

        self.elasticsearch = Elasticsearch(sniff_on_start=True)

    def search(self, request):
        '''docstring'''
        q = request.args.get('q')
        log.debug("Querying:" + q)
        G = nx.Graph()
        results = self.elasticsearch.search(index="lens",
                                            q=q,
                                            size=150000)

        for result in results['hits']['hits']:
            headline = result['_source']['headline']
            add_node(G, result['_id'], headline)
            for link in result['_source']['links']:
                doc, sentence = result['_id'].split("-")
                G.add_edge(int(doc), link[1])

        node_degress = []

        for node in G.nodes():
            node_degress.append((node, nx.degree(G, node)))

        nodes = sorted(node_degress, key=lambda node: node[1], reverse=True)

        headlines = nx.get_node_attributes(G, 'headline')

        output = []
        for node in nodes:
            try:
                item = (node[1], headlines[node[0]])
                output.append(item)
            except:
                pass
        return output

    def home(self):
        return ""
