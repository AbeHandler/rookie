'''
This module loads documents into whoosh and creates a sentence index
'''
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh import writing
from collections import defaultdict
from webapp import processed_location
import ipdb
import csv
import os
import sys
from itertools import tee, izip, islice, chain
csv.field_size_limit(sys.maxsize)

import ujson
import argparse
from dateutil.parser import parse


'''build connection to db'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import CONNECTION_STRING
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()


def getcorpusid():
    go = lambda *args: session.connection().execute(*args)
    for i in go("select corpusid from corpora where corpusname='{}'".format(args.corpus)):
        return i[0]


def stop_word(w):
    return False # TODO: corpus specific stop words


class Document(object):

    '''
    This is an abstraction over output from proc.document_parse()
    running in "pos" mode from the python NLP wrapper
    '''

    def __init__(self, json_output, coreferences=None):
        '''
        Initialize w/ the json output.
        Coreferences are optional
        '''
        try:
            sentences_json = json_output['sentences']
        except KeyError:
            sentences_json = []
        ngrams = []
        sentences = []
        for i in range(0, len(sentences_json)):
            sentence = Sentence(sentences_json[i], i)
            sentences.append(sentence)
            ngrams = ngrams + sentence.ngrams
        self.ngrams = ngrams
        self.sentences = sentences
        text = ""
        for sentence in self.sentences:
            text = text + " ".join([w.raw for w in sentence.tokens])
        self.full_text = text
        sentence_tokens = [s.tokens for s in self.sentences]
        self.tokens = list(chain(*sentence_tokens))


class Sentence(object):

    def get_ngrams(self):
        '''
        :param words: a list of all word tokens in a document
        :type words: Token
        '''
        ngrams = N_Grammer()
        grams = []
        # ngrams 1 thru 4
        for i in range(1, 5):
            grams = grams + ngrams.get_syntactic_ngrams(self.tokens, i)
        return grams

    def __init__(self, json_sentence, sentence_no):
        '''
        Initialize w/ the json output
        '''
        self.sentence_no = sentence_no
        tokens = json_sentence['tokens']
        lemmas = json_sentence['lemmas']
        poses = json_sentence['pos']
        assert len(tokens) == len(lemmas)
        assert len(poses) == len(lemmas)
        assert len(tokens) == len(poses)
        sentence_tokens = []
        for i in range(0, len(tokens)):
            t = Token(tokens[i], poses[i], lemmas[i], i, sentence_no)
            sentence_tokens.append(t)
        self.tokens = sentence_tokens
        self.ngrams = self.get_ngrams()

    def __repr__(self):
        return " ".join([i.raw for i in self.tokens])

class N_Grammer(object):

    '''
    Takes a line of output from python-Stanford wraper
    and finds the syntactically valid ngrams
    '''
    # https://stackoverflow.com/questions/21883108/fast-optimize-n-gram-implementations-in-python

    def pairwise(self, iterable, n=2):
        return izip(*(islice(it, pos, None) for pos, it
                      in enumerate(tee(iterable, n))))

    def get_ngrams(self, words, n=2):
        words = [i for i in words if not stop_word(i.raw.upper())]
        return self.pairwise(words, n)

    def is_syntactically_valid(self, ngram):
        valid_two_grams = ["NN", "AN"]  # , "NV", "VN"]
        valid_three_grams = ["AAN", "NNN", "ANN", "NPN"]  # , "ANV", "NNV", "NVV", "TVN", "VPN", "VNN", "VAN", "VDN"]
        valid_four_grams = ["ANPV", "NNNN", "ANNN"] # , "NNNV", "ANTV", "NNTV", "TVPN", "VANN", "VNNN", "VPNN"]

        pattern = "".join([(j.abreviated_pos()) for j in ngram])
        if pattern in valid_two_grams and len(pattern) == 2:
            return True
        if pattern in valid_three_grams and len(pattern) == 3:
            return True
        if pattern in valid_four_grams and len(pattern) == 4:
            return True

    def get_syntactic_ngrams(self, words, n):
        '''
        :param words: a list of word tokens
        :type words: Token
        '''
        return [i for i in self.get_ngrams(words, n) if
                self.is_syntactically_valid(i)]

class Token(object):

    def __init__(self, raw_token, pos, lemma_form, token_no, sentence_no):
        '''
        Initialize w/ the json output
        '''
        # Store tokens as unicode, but remove non standard chars for now #TODO
        self.raw = raw_token.encode("ascii", "ignore").decode()
        self.pos = pos
        self.lemma_form = lemma_form
        self.token_no = token_no
        self.sentence_no = sentence_no

    def abreviated_pos(self):
        if self.is_adjective():
            return "A"
        elif self.is_noun():
            return "N"
        elif self.is_preposition():
            return "P"
        elif self.is_verb():
            return "V"
        elif self.is_to():
            return "T"
        else:
            return "O"

    def is_adjective(self):
        if self.pos[0:2] == "JJ":
            return True
        else:
            return False

    def is_noun(self):
        if self.pos[0:2] == "NN":
            return True
        else:
            return False

    def is_preposition(self):
        if self.pos[0:2] == "IN":
            return True
        else:
            return False

    def is_verb(self):
        if self.pos[0:1] == "V":
            return True
        else:
            return False

    def is_to(self):
        if self.pos[0:2] == "TO":
            return True
        else:
            return False


def create_pubdate_index(metadata):
    '''
    Takes a dict of ngrams that shows which ngram in what pubdate.
    Inserts into db.
    '''
    go = lambda *args: session.connection().execute(*args)

    print "building pubdate index"
    # string to pubdate matrix created in building matrix
    for i,ngram in enumerate(metadata):
        dates = metadata[ngram]
        dates = sorted(set(dates))
        go(u"""INSERT INTO ngram_pubdates (ngram, pubdates, CORPUSID) VALUES (%s, %s, %s)""",
                ngram, ujson.dumps(dates), CORPUSID)

    print "\nindexing"
    go("create index on ngram_pubdates (ngram)")
    print "pubdate index built over %s terms" % (go("select count(1) from ngram_pubdates").fetchone()[0])


def load(index_location, processed_location):
    '''
    Load documents from procesed location into whoosh @ index_location
    '''

    s_counter = 0 # only increments when doc actually added to whoosh
    # w/o this kludge, doc ids cause index errors b/c loop counter higher b/c ~15 docs error on load

    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    ix = create_in(index_location, schema)
    writer = ix.writer()

    ngram_pubdate_index = defaultdict(list)

    people_org_ngram_index = {}
    go = lambda *args: session.connection().execute(*args)
    with open ("corpora/{}/processed/all.json".format(args.corpus)) as raw:
        for line in raw:
            line_json = ujson.loads(line)
            headline = line_json["headline"]
            try:
                pubdate = parse(line_json["pubdate"])
            except:
                tm = line_json["pubdate"].split("T")[0].strip('"') # wierdness i phone tweets
                pubdate = parse(tm)
            procesed_text = line_json["text"]

            try:
                url = line_json["url"]
            except KeyError:
                url = "unknown"
            doc = Document(procesed_text)
            full_text = doc.full_text
            ngrams = [unicode(" ".join(i.raw for i in j)) \
                                  for j in doc.ngrams]
            sentences = [(" ".join([j.raw for j in i.tokens]), [(j.raw, j.token_no) for j in i.tokens])\
                         for i in doc.sentences]
            if len(headline) > 0 and len(full_text) > 0:
                writer.add_document(title=headline, path=u"/" + str(s_counter), content=full_text)
                per_doc_json_blob = {'headline': headline, 'pubdate': pubdate.strftime('%Y-%m-%d'), 'ngrams': ngrams, "url": url, "sentences": sentences}
                go("""INSERT INTO doc_metadata (docid, data, corpusid) VALUES (%s, %s, %s)""", s_counter, ujson.dumps(per_doc_json_blob), CORPUSID)
                for ngram in ngrams:
                    ngram_pubdate_index[ngram].append(pubdate.strftime('%Y-%m-%d'))
                s_counter += 1
                if s_counter % 1000==0:
                    sys.stdout.write("...%s" % s_counter); sys.stdout.flush()
        create_pubdate_index(ngram_pubdate_index)
        writer.commit(mergetype=writing.CLEAR)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
    args = parser.parse_args()

    CORPUSID = getcorpusid()

    print "adding {} to whoosh and checking ngrams".format(args.corpus)

    directory = "indexes/" + args.corpus
    if not os.path.exists(directory):
        os.makedirs(directory)
    load(directory, args.corpus)
    session.commit()
