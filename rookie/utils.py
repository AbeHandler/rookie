import datetime
import networkx as nx

from nltk.corpus import stopwords
from elasticsearch import Elasticsearch
from stemming.porter2 import stem
from rookie import tagger_loc
from rookie import tagger_jar
from nltk.tag.stanford import POSTagger
from nltk.stem.wordnet import WordNetLemmatizer



def penn_to_wordnet(tag):
    '''
    Map a penn tag to a wordnet category
    '''
    tags = tuple(open("penn.txt", "r"))  # maps from penn tag to wordnet class
    tag = [t.split("\t")[2] for t in tags if t.split("\t")[0] == tag]
    return tag.pop().strip("\n")  # strip the newline character


def POS_tag(sentence):
    st = POSTagger(tagger_loc, tagger_jar)
    tags = st.tag(sentence.split())
    return tags


def get_stopwords():
    temp = stopwords.words("english")
    temp = temp + ['new', 'orleans', 'said', 'would', 'city', 'state',
                   'parish', 'louisiana', '', '|']
    temp = [stem(word) for word in temp]
    return temp


def query_results_to_bag_o_words(results):
    '''
    Takes a list of elastic search results and returns
    a bag of words
    :param request: Result objects
    :type request: list
    :returns: list. Naievely Tokenized words
    '''
    STOPWORDS = get_stopwords()
    bag_o_query_words = []
    for r in results:
        words = r.fulltext.split(" ")
        words = [word for word in words if word not in STOPWORDS]
        bag_o_query_words = bag_o_query_words + words
    return bag_o_query_words


def query_elasticsearch(lucene_query):
    ec = Elasticsearch(sniff_on_start=True)
    results = ec.search(index="lens",
                        q=lucene_query,
                        size=10000)['hits']['hits']
    return [Result(r) for r in results]


def get_node_degrees(results):

    G = nx.Graph()

    node_degrees = {}

    for result in results:
        if result.docid not in G.nodes():
            G.add_node(result.docid)
        for link in result.links:
            G.add_edge(result.docid, link[1])

        for node in G.nodes():
            node_degrees[node] = nx.degree(G, node)

    return node_degrees


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
        self.docid = self.nid
        self.links = result['_source']['links']
        self.score = result['_score']
        self.entities = result['_source']['entities']
        self.link_degree = None

    def as_dictionary(self):
        output = {}
        output['headline'] = self.headline
        output['timestamp'] = self.timestamp
        output['fulltext'] = self.fulltext
        output['url'] = self.url
        output['sentence_id'] = self.sentence_id
        output['link_degree'] = self.link_degree
        output['score'] = self.score
        output['entities'] = self.entities
        return output
