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

    def __init__(self, data):
        sentences = data['lines']['sentences']
        two_grams = []
        three_grams = []
        for sentence in sentences:
            for i in range(0, len(self.get_tokens(sentence['parse']))):
                print self.get_tokens(sentence['parse'])[i]
#                print sentence['lemmas'][i]
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

    def get_tokens(parse_string):
        pattern = "((?<=\()([A-Z]+\$?|\.) [^)^()]+(?=\)))"
        return re.findall(pattern, parse_string)

    def get_grams(self, s):
        tokens = self.get_tokens(s)
        twograms = [i for i in self.zipngram2(tokens)]
        twograms = [t for t in twograms if (self.is_adjective(t[0]) or
                    self.is_noun(t[0])) and self.is_noun(t[1])]
        twograms = [(t[0].split(" ")[1], t[1].split(" ")[1]) for t in twograms]

        threegrams = [i for i in self.zipngram2(tokens, 3)]

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


class Document(object):

    '''
    This is an abstraction over output from proc.document_parse()
    running in "ner" mode from the python NLP wrapper
    '''

    def __init__(self, json_output):
        '''
        Initialize w/ the json output
        '''
        sentences_json = json_output['sentences']
        sentences = []
        for sentence_json in sentences_json:
            sentence = Sentence(sentence_json)
            sentences.append(sentence)
        self.sentences = sentences


class Sentence(object):

    def get_ner(self, json_sentence, tokens):
        ner = json_sentence['ner']
        counter = 0
        output = []
        while counter < len(ner):
            ne_type = ner[counter]
            if ne_type != "O":
                ner_to_add = [tokens[counter]]
                try:
                    while ner[counter + 1] == ne_type:
                        ne_type = ner[counter + 1]
                        counter = counter + 1
                        next_token = tokens[counter]
                        ner_to_add.append(next_token)
                except IndexError:  # reached the end of the ner
                    pass
                output.append(NER(ner_to_add, ne_type))
            counter = counter + 1
        return output

    def __init__(self, json_sentence):
        '''
        Initialize w/ the json output
        '''
        tokens = json_sentence['tokens']
        lemmas = json_sentence['lemmas']
        poses = json_sentence['pos']
        assert(len(tokens) == len(lemmas))
        assert(len(poses) == len(lemmas))
        assert(len(tokens) == len(poses))
        sentence_tokens = []
        for i in range(0, len(tokens)):
            t = Token(tokens[i], poses[i], lemmas[i])
            sentence_tokens.append(t)
        self.tokens = sentence_tokens
        self.ner = self.get_ner(json_sentence, self.tokens)


class Token(object):

    def __init__(self, raw_token, pos, lemma_form):
        '''
        Initialize w/ the json output
        '''
        self.raw = raw_token
        self.pos = pos
        self.lemma_form = lemma_form


class NER(object):

    def __init__(self, tokens, type_of_ner):
        '''
        Initialize w/ the json output
        '''
        self.tokens = tokens
        self.type = type_of_ner
