"""
The web app that runs at vault.thelensnola.org/contracts.
"""
import datetime
import pdb

from rookie import (
    log
)

from elasticsearch import Elasticsearch
import networkx as nx
from rookie.utils import query_elasticsearch
from rookie.utils import Result

def add_node(G, nid, headline, timestamp, fulltext, url):
    doc_id, sentence_no = [int(i) for i in nid.split("-")]
    if doc_id == 2570:
        pdb.set_trace()
    if doc_id not in G.nodes():
        log.info("Adding {} {}".format(doc_id, timestamp))
        G.add_node(int(doc_id), headline=headline, timestamp=timestamp, fulltext=fulltext, url=url, sentencenos=sentence_no)
    return G


class Models(object):

    '''doctstring'''

    def __init__(self):
        '''docstring'''

        self.elasticsearch = Elasticsearch(sniff_on_start=True)

    def get_node_as_output(self, G, node):
    	print node
    	headlines = nx.get_node_attributes(G, 'headline')
        timestamps = nx.get_node_attributes(G, 'timestamp')
        fulltexts = nx.get_node_attributes(G, 'fulltext')
        urls = nx.get_node_attributes(G, 'url')
        sentencenos = nx.get_node_attributes(G, 'sentencenos')
    	pubdate = timestamps[node[0]].split(" ")[0]
        year, month, day = pubdate.split("-")
        pubdate = datetime.date(int(year), int(month), int(day))
        log.info(pubdate)
        node_id = node[0]
        item = [node_id, node[1], headlines[node_id],
                str(pubdate), fulltexts[node_id], urls[node_id], sentencenos[node_id]]
        return item

    def search(self, request):
        '''docstring'''
        
        output = []

        if request.args.get('q') is None:
            return output

        q = request.args.get('q')

        results = query_elasticsearch(q)

        G = nx.Graph()

        for result in results:
            G = add_node(result.docid)
            for link in result.links:
                G.add_edge(result.docid, link[1])

        node_degress = []
 
        for node in G.nodes():
            node_degress.append((node, nx.degree(G, node)))

        for node in node_degress:
            item = self.get_node_as_output(G, node)
            output.append(item)

        return output

    def home(self):
        return ""
