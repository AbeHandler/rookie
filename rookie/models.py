"""
The web app that runs at vault.thelensnola.org/contracts.
"""


from elasticsearch import Elasticsearch
import networkx as nx


def add_node(G, nid, headline):
    if nid not in G.nodes():
        G.add_node(int(nid), headline=headline)


class Models(object):

    '''doctstring'''

    def __init__(self):
        '''docstring'''

        self.elasticsearch = Elasticsearch(sniff_on_start=True)

    def search(self):
        '''docstring'''
        G = nx.Graph()
        results = self.elasticsearch.search(index="lens",
                                            q="Charter schools",
                                            size=150000)

        for result in results['hits']['hits']:
            headline = result['_source']['headline']
            add_node(G, result['_id'], headline)
            for link in result['_source']['links']:
                G.add_edge(int(result['_id']), link[1])

        node_degress = []

        for node in G.nodes():
            node_degress.append((node, nx.degree(G, node)))

        nodes = sorted(node_degress, key=lambda node: node[1], reverse=True)

        headlines = nx.get_node_attributes(G, 'headline')

        for node in nodes:
            try:
                print headlines[node[0]]
                print node
            except:
                pass
