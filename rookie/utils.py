import datetime
import networkx as nx

from elasticsearch import Elasticsearch


def query_elasticsearch(lucene_query):
    ec = Elasticsearch(sniff_on_start=True)
    results = ec.search(index="lens", q=lucene_query)['hits']['hits']
    return results


def get_node_degress(results):

    G = nx.Graph()

    for result in results:
        if result.docid not in G.nodes():
            G.add_node(result.docid)
        for link in result.links:
            G.add_edge(result.docid, link[1])

        node_degress = []

        for node in G.nodes():
            node_degress.append((node, nx.degree(G, node)))

    return node_degress


class Link(object):

    def __init__(self, link):
        '''Initialize with a result'''

        self.link_text = link[0]
        self.link_num = link[1]


class Result(object):

    '''An elastic search result'''

    def __init__(self, result):
        '''Initialize with a result'''

        self.headline = result['_source']['headline'].encode('ascii', 'ignore')
        timestamp = result['_source']['timestamp'].encode('ascii', 'ignore')
        timestamp = timestamp.split(" ")[0]
        year, month, day = timestamp.split("-")
        pubdate = datetime.date(int(year), int(month), int(day))
        self.timestamp = pubdate
        fulltext = result['_source']['full_text'].encode('ascii', 'ignore')
        self.fulltext = fulltext
        self.url = result['_source']['url'].encode('ascii', 'ignore')
        self.nid = result['_id'].encode('ascii', 'ignore')
        self.docid = int(self.nid.split("-")[0])
        self.links = result['_source']['links']
