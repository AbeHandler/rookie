import datetime
import json
import re
import pdb

from itertools import tee, izip, islice


class N_Grammer(object):

    '''
    Takes a line of output from python-Stanford wraper
    and finds the syntactically valid ngrams
    '''
    # https://stackoverflow.com/questions/21883108/fast-optimize-n-gram-implementations-in-python

    # valid_two_grams = ["NN", "AN"]
    # valid_three_grams = ["AAN", "NNN", "ANN"]

    # A = any adjective (PTB tag starts with JJ)
    # N = any noun (PTB tag starts with NN)

    def __init__(self, filename):
        with open(filename, 'r') as processed:
            data = json.load(processed)
            sentences = data['lines']['sentences']
            two_grams = []
            three_grams = []
            for sentence in sentences:
                grams = self.get_grams(sentence['parse'])
                two_grams = two_grams + grams[0]
                three_grams = three_grams + grams[1]
            self.twograms = two_grams
            self.threegrams = three_grams

    def is_adjective(self, t):
        if t[0:2] == "JJ":
            return True
        else:
            return False

    def is_noun(self, t):
        if t[0:2] == "NN":
            return True
        else:
            return False

    def pairwise(self, iterable, n=2):
        return izip(*(islice(it, pos, None) for pos, it
                      in enumerate(tee(iterable, n))))

    def zipngram2(self, words, n=2):
        return self.pairwise(words, n)

    def get_grams(self, s):
        p = "((?<=\()[A-Z]+ [^)^()]+(?=\)))"
        twograms = [i for i in self.zipngram2(re.findall(p, s))]
        twograms = [t for t in twograms if (self.is_adjective(t[0]) or
                    self.is_noun(t[0])) and self.is_noun(t[1])]
        twograms = [(t[0].split(" ")[1], t[1].split(" ")[1]) for t in twograms]

        threegrams = [i for i in self.zipngram2(re.findall(p, s), 3)]

        threegrams = [t for t in threegrams if self.is_noun(t[2]) and
                      (
                       (self.is_noun(t[1]) and self.is_noun(t[0])) or
                       (self.is_adjective(t[1]) and self.is_adjective(t[0])) or
                       (self.is_noun(t[1]) and self.is_adjective(t[0]))
                      )]
        threegrams = [(t[0].split(" ")[1], t[1].split(" ")[1],
                      t[2].split(" ")[1])
                      for t in threegrams]

        return (twograms, threegrams)


class Link(object):

    def __init__(self, link):
        '''Initialize with a result'''

        self.link_text = link[0]
        self.link_num = link[1]


class EntityCount(object):

    def __init__(self, tup, timestamps=None):
        '''A named entity, and how many times it shows up in query'''

        self.name = tup[0]
        self.count = tup[1]
        # pub date of each time entity shows up in results
        self.timestamps = timestamps


class QueryResult(object):

    def __init__(self, bigrams, trigrams, entity_dict, results):
        '''Output from an elastic search query'''

        self.bigrams = bigrams
        self.trigrams = trigrams
        self.persons = entity_dict['PERSON']
        self.organizations = entity_dict['ORGANIZATION']
        self.locations = entity_dict['LOCATION']
        self.money = entity_dict['MONEY']
        self.dates = entity_dict['DATE']
        self.results = results


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
        self.trigrams = result['_source']['three_grams']
        self.bigrams = result['_source']['two_grams']
