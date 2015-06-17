import networkx as nx
import string
import collections
import pdb
from rookie import log
from nltk.corpus import stopwords
from elasticsearch import Elasticsearch
from rookie.classes import Result
from rookie.classes import QueryResult
from rookie.classes import EntityCount
from repoze.lru import lru_cache


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
                   'parish', 'louisiana', '', '|', 'said', 'say', 'story',
                   'we', 'cover', 'lens']
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


def get_timestamps(name, type_entity, results):
    timestamps = [r['_source']['timestamp'] for r in results if name
                  in r['_source']['entities'][type_entity]]
    return timestamps


def get_entity_counts(entities, etype, results):
    ents = [EntityCount(e) for e in
            collections.Counter(entities[etype]).most_common(25)]
    for e in ents:
        e.timestamps = get_timestamps(e.name, etype, results)
    return ents


def get_word_counts(results):
    bag = query_results_to_bag_o_words(results)
    words = collections.Counter(bag).most_common(25)
    word_entities = []
    for word in words:
        timestamps = [r['_source']['timestamp'] for r in results if word[0]
                      in r['_source']['full_text']]
        word_entities.append(EntityCount(word, timestamps))
    return word_entities


# @lru_cache(maxsize=10000)
def query_elasticsearch(lucene_query):
    log.info("querying elastic search")
    ec = Elasticsearch(sniff_on_start=True)
    results = ec.search(index="lens",
                        q=lucene_query,
                        size=10000)['hits']['hits']
    entities = query_results_to_bag_o_entities(results)
    keys = ["PERSON", "LOCATION", "MONEY", "DATE", "ORGANIZATION"]
    entity_dict = {}
    for key in keys:
        entity_dict[key] = get_entity_counts(entities, key, results)
    words = get_word_counts(results)
    results = [Result(r) for r in results]
    query_result = QueryResult(words, entity_dict, results)
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
