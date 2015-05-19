"""
The web app that runs at vault.thelensnola.org/contracts.
"""
import datetime

from rookie import (
    log
)

from elasticsearch import Elasticsearch
import networkx as nx


def add_node(G, nid, headline, timestamp):
    if nid not in G.nodes():
        doc, sentence = nid.split("-")
        G.add_node(int(doc), headline=headline, timestamp=timestamp)


class Models(object):

    '''doctstring'''

    def __init__(self):
        '''docstring'''

        self.elasticsearch = Elasticsearch(sniff_on_start=True)

    def search(self, request):
        '''docstring'''
        q = request.args.get('q')

        output = []

        if q is None:
            return output

        log.debug("Querying:" + q)
        G = nx.Graph()
        results = self.elasticsearch.search(index="lens",
                                            q=q,
                                            size=150000)

        for result in results['hits']['hits']:
            headline = result['_source']['headline']
            timestamp = result['_source']['timestamp']
            add_node(G, result['_id'], headline, timestamp)
            for link in result['_source']['links']:
                doc, sentence = result['_id'].split("-")
                G.add_edge(int(doc), link[1])

        node_degress = []

        for node in G.nodes():
            node_degress.append((node, nx.degree(G, node)))

        nodes = sorted(node_degress, key=lambda node: node[1], reverse=True)

        headlines = nx.get_node_attributes(G, 'headline')
        timestamps = nx.get_node_attributes(G, 'timestamp')

        for node in nodes:
            try:
                pubdate = timestamps[node[0]].split(" ")[0]
                year, month, day = pubdate.split("-")
                pubdate = datetime.date(int(year), int(month), int(day))
                print pubdate
                log.info(pubdate)
                item = (node[1], headlines[node[0]],
                        str(pubdate))
                output.append(item)
            except:
                pass

        output.sort(key=lambda tup: tup[0], reverse=True)

        output = output[0:10]

        output.sort(key=lambda tup: tup[2], reverse=False) # sort by pubdate
        return output

    def home(self):
        return ""
