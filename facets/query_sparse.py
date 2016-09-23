'''
Queries whoosh and builds facets for query
'''
from __future__ import division
from pylru import lrudecorator
from whoosh.index import open_dir
from collections import defaultdict
import operator
import datetime
import ipdb
import time
import cPickle as pickle
import argparse

from facets.merger import merge_terms
from dateutil.parser import parse
from Levenshtein import distance

DEBUG = False

#CUTOFF = 50

def make_stops():
    stops_ = ["lens staff", "last month", "last week", "last year", "lens staff writer", "live blog", "#### live", "matt davis", "ariella cohen", "story report", "####", "#### live blog", "the lens", "new orleans", "staff writer", "orleans parish"]
    stops_ = stops_ + ["last year", "last week", "last month", "next week", "last week"]
    for o1 in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]:
        for o2 in ["years", "year", "month", "months", "day", "days", "week", "weeks"]:
            stops_.append(o1 + " " + o2)


    stops_ = stops_ + ["first time", "second time", "York Times", "recent years", "same time"]

    return set(stops_)

stops = make_stops()

import whoosh.query


def stop(w):
    if w in stops:
        return True
    if "last year" in w:
        return True

'''build connection to db'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import CONNECTION_STRING
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()

def getcorpusid(corpus):
    go = lambda *args: session.connection().execute(*args)
    for i in go("select corpusid from corpora where corpusname='{}'".format(corpus)):
        return i[0]

def load_sparse_vector_data_structures(corpus):
    corpusid = getcorpusid(corpus)
    output = {}
    results = session.connection().execute("select * from count_vectors where corpusid='{}'".format(corpusid))
    for i, row in enumerate(results):
        # row = (doc id, corpus id, data)
        output[unicode(row[0])] = row[2].keys() # raw form ==> [u'34986', u'20174' ... u'6664']
    return output

def filter_by_date(results, corpus, start_d, end_d):
    '''return results that fall in a date range'''
    if start_d is not None and end_d is not None:
        return [r for r in results if load_all_data_structures(corpus)["pubdates"][int(r)] > start_d
                and load_all_data_structures(corpus)["pubdates"][int(r)] < end_d]
    else:
        return results

@lrudecorator(100)
def get_ndocs(corpus):
    index = open_dir("indexes/{}/".format(corpus))
    with index.searcher() as s:
        results = s.search(whoosh.query.Every(), limit=None)
    return len(results)  # TODO: how many docs are indexed in whoosh?


def debug_print(msg):
    if DEBUG:
        print msg

@lrudecorator(100)
def load_all_data_structures(corpus):
    '''
    Load everything indexed in build_matrix.py
    '''
    decoders = {}
    reverse_decoders = {}
    df = {}
    idf = {}
    n = "ngram"
    decoder = pickle.load(open("indexes/{}/{}_key.p".format(corpus, n), "rb"))
    decoder_r = {v: k for k, v in decoder.items()}
    decoders[n] = decoder
    reverse_decoders[n] = decoder_r
    df[n] = pickle.load(open("indexes/{}/{}_df.p".format(corpus, n), "rb"))
    idf[n] = pickle.load(open("indexes/{}/{}_idf.p".format(corpus, n), "rb"))
    pubdates = pickle.load(open("indexes/{}/pubdates_xpress.p".format(corpus, n), "rb"))
    vectors = load_sparse_vector_data_structures(corpus)
    return {"pubdates": pubdates, "vectors": vectors, "decoders": decoders, "reverse_decoders": reverse_decoders, "df": df, "idf": idf}


def get_jaccard(one, two):
    one = set([i.lower() for i in one.split(" ")])
    two = set([i.lower() for i in two.split(" ")])
    jacard = float(len(one & two)) / len(one | two)
    return jacard


def matching(a, b):
    if a.lower() in b.lower() or b.lower() in a.lower(): # substring
        return True
    if get_jaccard(a, b) >= .3:
        return True
    if distance(a, b) < 3:
        return True
    return False

def cluster(raw_facets, structures, q, K):
    '''K is how many clusters needed'''
    clusters = []

    for facet in raw_facets:
        raw, score = facet # just string, no score. raws are tuples: string, score

        matches = [o for o in clusters for s in o if matching(s[0], raw)]
        if len(matches) == 0:
            clusters.append([(raw, score)])
        elif len(matches) == 1:
            cluster = matches.pop()
            cluster.append((raw, score))
        if len(clusters) == K:
            return clusters
    return clusters



def get_facet_tfidf_cutoff(results, structures, facet_type, n_facets):
    '''
    get the tfidf score for each facet_type w/ a cutoff
    "tf" = how many queried documents contain f (i.e. boolean: facet occurs or no)
    "df" = how many total documents contain f (i.e. boolean: facet occurs or no)
    "tfidf" = np.multiply(tf, np.log(1./df))

    returns the top CUTOFF indexes in the array
    '''
    tfs = defaultdict(int)
    for r in results:
        n_counts = structures["vectors"][r]
        for n in n_counts:
            tfs[n] += 1
    
    tfidfs = defaultdict(int)
    idf = structures["idf"][facet_type]
    for t in tfs:
        tfidfs[t] = idf[int(t)] * tfs[t]
    # ipdb.set_trace()
    sorted_x = sorted(tfidfs.items(), key=operator.itemgetter(1), reverse=True)[0:n_facets]
    return [(structures["reverse_decoders"][facet_type][int(i[0])], i[1]) for i in sorted_x] # i[0] is ngram, i[1] is tfidf score



def get_facets_for_q(q, results, n_facets, structures):
    '''
    Provide q, set of results and n_facets. 

    Return binned facets. 
    '''

    if len(results) == 0:
        return []

    raw_facets = get_facet_tfidf_cutoff(results, structures, "ngram", n_facets)

    # exclude facets that are direct substrings of q
    raw_facets = [o for o in raw_facets if o[0].lower() not in q and q not in o[0].lower()]
    clusters = cluster(raw_facets, structures, "ngram", n_facets)
    out = []
    for cluster_ in clusters:
        numbers = [(structures["decoders"]["ngram"][o[0]], o[0]) for o in cluster_]
        counts = [(structures["df"]["ngram"][c[0]], c[1]) for c in numbers]
        max_c = max(counts, key=lambda x:x[0])
        if max_c[1] == "Bashar Assad":
            ipdb.set_trace()
        dd = q.lower().encode("ascii", "ignore")
        if not matching(max_c[1].lower(), dd):
            out.append(max_c[1])

    return {"g": [i.encode("ascii", "ignore") for i in out]}



if __name__ == '__main__':

    from webapp.models import query
    parser = argparse.ArgumentParser(description='parser')
    parser.add_argument("-v", action="store_true", default=False, help="verbose")
    parser.add_argument('-q', '--query', dest='query')
    parser.add_argument('-c', '--corpus', dest='corpus')
    parser.add_argument('-t', '--time', dest='time', default=None, help="parseable dates, split by #")


    args = parser.parse_args()
    
    if args.time is not None:
        start, end = [parse(a) for a in args.time.split("##")]
    else:
        start, end = [None, None]

    if args.v:
        DEBUG = True
    else:
        DEBUG = False

    CORPUS = args.corpus
    NDOCS = get_ndocs(CORPUS)

    aliases = defaultdict(list)

    DEBUG = False # by default false. can be set to T w/ arg -v in command line mode

    CORPUS_ID = getcorpusid(CORPUS)

    RESULTZ = filter_by_date(query(args.query, args.corpus), args.corpus, start, end)

    structures = load_all_data_structures(CORPUS)
    startTime = time.time()
    facets = get_facets_for_q(args.query, RESULTZ, 50, structures)
    print facets

session.close()