'''
Queries whoosh and builds facets for query
'''
from __future__ import division
from pylru import lrudecorator
from webapp.models import query
import bottleneck
from webapp.models import get_doc_metadata
from dateutil.parser import parse
from whoosh.index import open_dir
from collections import defaultdict
import operator
import ujson
import joblib
import numpy as np
import ipdb
import time
import itertools
import cPickle as pickle
import sys
import argparse
from webapp import CORPUS
from Levenshtein import distance


stops = ["lens staff", "lens staff writer", "live blog", "#### live", "matt davis", "ariella cohen", "story report", "####", "#### live blog", "the lens", "new orleans", "staff writer", "orleans parish"]

import whoosh.query

'''build connection to db'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp.classes import CONNECTION_STRING
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()


def load_sparse_vector_data_structures():
    print "loading all sparse vectors"
    output = {}
    results = session.connection().execute("select * from count_vectors")
    for i, row in enumerate(results):
        output[unicode(row[0])] = row[1].keys() # raw form ==> [u'34986', u'20174' ... u'6664']
    return output

VECTORS = load_sparse_vector_data_structures()

@lrudecorator(100)
def get_ndocs(corpus):
    index = open_dir("indexes/{}/".format(corpus))
    with index.searcher() as s:
        results = s.search(whoosh.query.Every(), limit=None)
    return len(results)  # TODO: how many docs are indexed in whoosh?

NDOCS = get_ndocs(CORPUS)

STOPTOKENS = ["new", "orleans"]

aliases = defaultdict(list)

CUTOFF = 25

DEBUG = False # by default false. can be set to T w/ arg -v in command line mode


def debug_print(msg):
    if DEBUG:
        print msg

@lrudecorator(100)
def load_all_data_structures():
    '''
    Load everything indexed in build_matrix.py
    '''
    decoders = {}
    reverse_decoders = {}
    matrixes = {}
    df = {}
    idf = {}
    for n in ["ngram"]:
        decoder = pickle.load(open("indexes/{}/{}_key.p".format(CORPUS, n), "rb"))
        decoder_r = {v: k for k, v in decoder.items()}
        decoders[n] = decoder
        reverse_decoders[n] = decoder_r
        df[n] = pickle.load(open("indexes/{}/{}_df.p".format(CORPUS, n), "rb"))
        idf[n] = pickle.load(open("indexes/{}/{}_idf.p".format(CORPUS, n), "rb"))
    return {"decoders": decoders, "reverse_decoders": reverse_decoders, "df": df, "idf": idf}


def s_check(facet, proposed_new_facet, distance):
    '''
    Checks possessive affix. 

    If proposed new facet is just facet + "s", return True
    '''
    if distance != 1:
        return False
    if proposed_new_facet[-1:] == "s" and facet[-1:] != "s":
        return True
    return False


def get_jaccard(one, two):
    one = set([i.lower() for i in one.split(" ") if i.lower() not in STOPTOKENS])
    two = set([i.lower() for i in two.split(" ") if i.lower() not in STOPTOKENS])
    jacard = float(len(one & two)) / len(one | two)
    return jacard


def heuristic_cleanup(output, proposed_new_facet, structures, q):
    '''
    An ugly heuristic that tries to filter out bad/meaningless facets quickly

    Facet problems:
       - an 's at the end of a facet (Mitch Landrieu's vs. Mitch Landrieu)
       - overlapping facets (Orleans Police vs. New Orleans Police)
       - "Split" facets (Mayor Mitch vs. Mitch Landrieu)
       - Meaningless facets in a stop list ("new orleans", "the lens", "staff writer")
    
    The facet algorithm makes greedy calls to heuristic_cleanup. Each time heuristic_cleanup
    is called, the param output should be a list of good, meaningful facets for Q. This function
    will replace good facets w/ better param:proposed_new_facet if appropriate

    Returns output again, possibly improved/lengthened
    '''
    debug_print("processing {}".format(proposed_new_facet))
    debug_print("thus far have:")
    debug_print(output)
    dfs = structures["df"]["ngram"]
    decoder = structures["decoders"]["ngram"]
    if proposed_new_facet.lower() in stops:
        return output # dont and the new facet
    if proposed_new_facet in output:
        return output # dont add duplicates
    if "new" in proposed_new_facet.lower():
        return output
    if get_jaccard(proposed_new_facet, q) > .5:
        return output # proposed new facet overlaps w/ query
    append = True # insert the facet after the check. assume true
    for index, facet in enumerate(output): # loop over facets thus far
        dist = distance(facet, proposed_new_facet) # get lev distance
        if dist > 0 and dist < 3: # if lev. distance is less than 2
            # if the proposed facet is longer than the good one
            # the [-1:] below prevents replacing "Mitch Landrieu" w/ "Mitch Landrieus"
            if s_check(facet, proposed_new_facet, dist):
                append = False
            elif (len(proposed_new_facet) > len(facet)):
                #print "proposed"
                #print dfs[decoder[proposed_new_facet]]
                #print "new"
                #print dfs[decoder[proposed_new_facet]]
                debug_print("replacing {} with {}".format(output[index], proposed_new_facet))
                output[index] = proposed_new_facet
                append = False
        if get_jaccard(proposed_new_facet, facet) > .5:
            #print "proposed"
            #print [decoder[proposed_new_facet]]
            #print "new"
            #print [decoder[proposed_new_facet]]
            if len(proposed_new_facet) > len(facet):
                debug_print("replacing {} with {}".format(output[index], proposed_new_facet))
                output[index] = proposed_new_facet
            else:
                debug_print("{} overlaps w/ {} but is shorter. don't append".format(proposed_new_facet, output[index]))

            # don't append even if new facet does not replace a given facet (in lines above). 
            # this is because new facet is too similar to some existing facet
            append = False
        if proposed_new_facet.split(" ")[0].lower() == facet.split(" ").pop().lower():
            joined = " ".join(facet.split(" ")[:-1]) + " " + proposed_new_facet
            try:
                count_joined = dfs[decoder[joined]]
                count_original = dfs[decoder[output[index]]]
                if count_original > count_joined * 2:
                     pass
                else:
                    debug_print("parse/merge. replacing {} c.{} with {} c.{}".format(output[index], count_original, joined, count_joined))
                    aliases[joined] = aliases[output[index]] + [output[index]]
                    output[index] = joined
                    new_this_round = joined
                    append = False
            except KeyError:
                pass # a key error here means the facet does not occur in the corpus

    if append:
        debug_print("appending {}".format(proposed_new_facet))
        output.append(proposed_new_facet)
    return [i for i in set(output)] #sometimes more than 1 facet will be replaced by propsed_new_facet


def get_all_facets(raws, structures, facet_type, q):
    '''
    :param indices: ?
    :param structures: data structures for facets
    :param facet_type: could be people/ngram/org but will always = ngram basically
    :param q: query
    :return:
    '''
    output = []
    for facet_bin in raws:
        for possible_f in raws[facet_bin]:
            output = heuristic_cleanup(output, possible_f, structures, q)
    print "best after heuristic_cleanup"
    print output


def get_facet_tfidf_cutoff(results, structures, facet_type, cutoff):
    '''
    get the tfidf score for each facet_type w/ a cutoff
    "tf" = how many queried documents contain f (i.e. boolean: facet occurs or no)
    "df" = how many total documents contain f (i.e. boolean: facet occurs or no)
    "tfidf" = np.multiply(tf, np.log(1./df))

    returns the top CUTOFF indexes in the array
    '''
    start_time = time.time()
    tfs = defaultdict(int)
    print "found {}".format(len(results))
    for r in results:
        n_counts = VECTORS[r]
        for n in n_counts:
            tfs[n] += 1
    sorted_tfs = sorted(tfs.items(), key=operator.itemgetter(1), reverse=True)[0:CUTOFF]
    sorted_tfs = [structures["reverse_decoders"][facet_type][int(i[0])] for i in sorted_tfs] # i[0] is ngram, i[1] is tfidf score
    print "best by raw count"
    print sorted_tfs
    tfidfs = defaultdict(int)
    idf = structures["idf"][facet_type]
    for t in tfs:
        tfidfs[t] = idf[int(t)] * tfs[t]
    sorted_x = sorted(tfidfs.items(), key=operator.itemgetter(1), reverse=True)[0:CUTOFF]
    sorted_x = [structures["reverse_decoders"][facet_type][int(i[0])] for i in sorted_x] # i[0] is ngram, i[1] is tfidf score
    print "best by td idf"
    print sorted_x
    return sorted_x
    # print tfidfs


def filter_t(results, start, end, structures):
    '''
    Take a set of results and return those that fall in [start, end]
    '''
    return [i for i in results if parse(get_doc_metadata(i)["pubdate"]) >= start and parse(get_doc_metadata(i)["pubdate"]) <= end]


def get_raw_facets(results, bins, structures):
    '''
    Returns top_n facets per bin + top_n for global bin
    '''
    raw_results = {} # raw best facets by tf idf

    raw_results["g"] = get_facet_tfidf_cutoff(results, structures, "ngram", CUTOFF)

    #for yr in bins:
    #    lresults = filter_t(results, parse("{}-01-01".format(yr)),
    #                        parse("{}-01-01".format(yr+1)), structures)
    #    raw_results[yr] = get_facet_tfidf_cutoff(lresults, structures, "ngram", CUTOFF)

    return raw_results


def get_facets_for_bin(tfidfs, structures, ok_facets, n_facets):
    '''
    Given a list of tfidf scores, a list of ok_facets, n_facets
    '''
    tfidfs.sort(key=lambda x: x[1]) # sort by score (they are top N in a partsort)
    output = []
    for facet_name in tfidfs:
        if facet_name in ok_facets:
            output.append(facet_name)
        if len(output) == n_facets:
            return output
    return output


def get_facets_for_q(q, results, n_facets):
    '''
    Provide q, set of results and n_facets. 

    Return binned facets. TODO: xrange(2010, 2016) hardcodes bins for now 
    '''

    structures = load_all_data_structures()

    facet_results = defaultdict(list) # results per bin. output.

    # TODO binning
    # Get raw facets by tfidf score 
    raw_results = get_raw_facets(results, xrange(2010, 2012), structures)

    # Get all of the possible facets
    ok_facets = get_all_facets(raw_results, structures, "ngram", q)

    #for t_bin in raw_results: # for each bin
    #    facet_results[t_bin] = get_facets_for_bin(raw_results[t_bin], structures, ok_facets, n_facets)
    print ok_facets

    return facet_results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='parser')
    parser.add_argument("-v", action="store_true", default=False, help="verbose")
    parser.add_argument('-q', '--query', dest='query')
    parser.add_argument('-c', '--corpus', dest='corpus')
    args = parser.parse_args()

    if args.v:
        DEBUG=True
    else:
        DEBUG=False

    CORPUS = args.corpus
    RESULTZ = query(args.query)
    print get_facets_for_q(args.query, RESULTZ, 9)