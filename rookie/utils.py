import networkx as nx
import string
import collections
import pdb
from flask.ext.cache import Cache
from nltk.corpus import stopwords
from elasticsearch import Elasticsearch
from rookie.classes import Result
from rookie.classes import QueryResult
from rookie.classes import EntityCount

# cache = Cache(config={'CACHE_TYPE': 'simple'})


def query_results_to_bag_o_entities(results):
    '''
    Return a bag of entities
    '''

    bag_o_entities = {}

    bag_o_keys = ['TIME', 'LOCATION', 'ORGANIZATION', 'PERSON', 'MONEY',
                  'PERCENT', 'NUMBER', 'DATE']

    for key in bag_o_keys:
        bag_o_entities[key] = []

    for r in results:
        entities = r['_source']['entities']
        keys = entities.keys()
        for key in keys:
            bag_o_entities[key] = bag_o_entities[key] + entities[key]

    return bag_o_entities


def get_stopwords():
    temp = stopwords.words("english")
    temp = temp + ['new', 'orleans', 'said', 'would', 'city', 'state',
                   'parish', 'louisiana', '', '|', 'said', 'say']
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
    for result in results:
        words = result['_source']['full_text'].split(" ")
        words = [word for word in words if word not in STOPWORDS]
        bag_o_query_words = bag_o_query_words + words
    return bag_o_query_words


# @cache.memoize(10000)
def query_elasticsearch(lucene_query):
    ec = Elasticsearch(sniff_on_start=True)
    results = ec.search(index="lens",
                        q=lucene_query,
                        size=10000)['hits']['hits']
    entities = query_results_to_bag_o_entities(results)
    persons = [EntityCount(e) for e in
               collections.Counter(entities['PERSON']).most_common(25)]
    orgs = [EntityCount(e) for e in
            collections.Counter(entities['ORGANIZATION']).most_common(25)]
    locations = [EntityCount(e) for e in
                 collections.Counter(entities['LOCATION']).most_common(25)]
    money = [EntityCount(e) for e in
             collections.Counter(entities['MONEY']).most_common(25)]
    dates = [EntityCount(e) for e in
             collections.Counter(entities['DATE']).most_common(25)]
    bag = query_results_to_bag_o_words(results)
    words = collections.Counter(bag).most_common(25)
    results = [Result(r) for r in results]
    query_result = QueryResult(words, persons, orgs,
                               locations, money, dates, results)
    return query_result


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


def clean_punctuation(input_string):
    '''
    Assumes ASCII input. TODO: Error handling.
    '''
    for punctuation in string.punctuation:
        input_string = input_string.replace(punctuation, "")
    return input_string
