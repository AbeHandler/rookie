import string
import collections
import nltk
import pickle
import redis
import math
import pdb
import itertools
from time import gmtime, strftime
from rookie import log
from nltk.corpus import stopwords
from elasticsearch import Elasticsearch
from rookie.classes import Result
from rookie.classes import QueryResult
from rookie.classes import EntityCount
from repoze.lru import lru_cache
import datetime


REDIS = redis.StrictRedis(host='localhost', port=6379, db=0)


def load_ngrams(number):
    to_cache = get_corpus_counts(number)
    for k in to_cache.keys():
        log.info("caching | {} | {}").format(" ".join(k), to_cache[k])
        REDIS.set(" ".join(k), to_cache[k])


def load_cache():
    load_ngrams("1")
    load_ngrams("2")
    load_ngrams("3")


@lru_cache(maxsize=10000)
def get_grams(text):
    unigrams = text.split(" ")
    bigrams = nltk.bigrams(unigrams)
    trigrams = nltk.trigrams(unigrams)
    return (unigrams, bigrams, trigrams)


def get_full_text(data):
    try:
        sentences = data['lines']['sentences']
        full_text = []
        for sentence in sentences:
            full_text = full_text + sentence['lemmas']
        full_text = " ".join(full_text).encode('ascii', 'ignore').lower()
        full_text = clean_punctuation(full_text)
        return full_text
    except TypeError:
        return ""


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


def time_stamp_to_date(timestamp):
    timestamp = timestamp.split(" ")[0]
    yr = int(timestamp.split("-")[0])
    mo = int(timestamp.split("-")[1])
    dy = int(timestamp.split("-")[2])
    return datetime.date(yr, mo, dy)


def get_timestamps(name, type_entity, results):
    timestamps = [time_stamp_to_date(r['_source']['timestamp']) for r in
                  results if name
                  in r['_source']['entities'][type_entity]]
    return timestamps


def get_entity_counts(entities, etype, results):
    ents = [EntityCount(e) for e in
            collections.Counter(entities[etype]).most_common(25)]
    for e in ents:
        e.timestamps = get_timestamps(e.name, etype, results)
    return ents


@lru_cache(maxsize=10000)
def get_corpus_counts(grams):
    fname = "data/{}-grams.p".format(grams)
    with open(fname, "rb") as gram_file:
        grams = pickle.load(gram_file)
    return grams


def get_word_counts(results):
    bag = query_results_to_bag_o_words(results)
    words = collections.Counter(bag).most_common(25)
    word_entities = []
    for word in words:
        timestamps = [time_stamp_to_date(r['_source']['timestamp'])
                      for r in results if word[0]
                      in r['_source']['full_text']]
        word_entities.append(EntityCount(word, timestamps))
    return word_entities


@lru_cache(maxsize=10000)
def get_denominator(counter_keys_len, delta):
    return math.log(float(counter_keys_len + delta))


# counter can be either phrase or corpus wide
def lidstone(phrase, counter, delta):
    try:
        numerator = math.log(float(counter[phrase] + delta))
        denominator = get_denominator(len(counter.keys()), delta)
        lidstone = numerator / denominator
        return lidstone
    except KeyError:
        return 0


def get_lidstones(query_counter, corpus_counter):
    delta = .5
    lidstone_output = []
    print str(len(query_counter.keys())) + " to check"
    for phrase in query_counter.keys():
        if all(len(i) > 0 for i in phrase):
            p_phrase_given_corpus = lidstone(phrase, corpus_counter, delta)
            p_phrase_given_query = lidstone(phrase, query_counter, delta)
            if p_phrase_given_corpus == 0:
                lidstone_output.append((phrase, 0))
            else:
                lidstone_output.append((phrase, p_phrase_given_query /
                                       p_phrase_given_corpus))
    return lidstone_output


def list_to_counter(input):
    trigrams = list(itertools.chain(*input))
    trigrams = [tuple(x) for x in trigrams]
    trigrams = collections.Counter(trigrams)
    trigrams = collections.Counter(el for el in trigrams.elements()
                                   if trigrams[el] > 2)
    return trigrams


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
    results = [Result(r) for r in results]

    trigrams = [r.trigrams for r in results]
    trigrams = list_to_counter(trigrams)

    bigrams = [r.bigrams for r in results]
    bigrams = list_to_counter(bigrams)

    query_result = QueryResult(bigrams, trigrams,
                               entity_dict, results)
    log.debug(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    return query_result


def clean_punctuation(input_string):
    '''
    Assumes ASCII input. TODO: Error handling.
    '''
    for punctuation in string.punctuation:
        input_string = input_string.replace(punctuation, " ")
    return input_string
