'''
Queries whoosh and builds facets for query
'''
from __future__ import division
from pylru import lrudecorator
from whoosh.index import open_dir
from collections import defaultdict
import operator
import datetime
import time
import cPickle as pickle
import argparse
from Levenshtein import distance

DEBUG = False
STOPTOKENS = [] # TODO: set this in the db

CUTOFF = 50

stops = ["lens staff", "lens staff writer", "live blog", "#### live", "matt davis", "ariella cohen", "story report", "####", "#### live blog", "the lens", "new orleans", "staff writer", "orleans parish"]

import whoosh.query

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


def heuristic_cleanup(output, proposed_new_facet, structures, q, aliases=defaultdict(list)):
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
    if proposed_new_facet.lower() == "last year":
        return output
    if proposed_new_facet.lower() == "next year":
        return output
    if proposed_new_facet.lower() in q.lower(): # if new facet is a substring of Q, reject
        return output
    if q.lower() in proposed_new_facet.lower(): # if q is substring of proposed facet, reject
        return output
    if get_jaccard(proposed_new_facet, q) >= .33:
        return output # proposed new facet overlaps w/ query
    
    def is_in_output(output, proposed_new_facet):
        return [o for o in output if (proposed_new_facet in o or o in proposed_new_facet)]
        
    # overlapping facets
    overlaps = is_in_output(output, proposed_new_facet)

    if len(overlaps) > 0:
        overlaps_and_counts = [(ovlps, dfs[decoder[ovlps]]) for ovlps in overlaps]
        max_overlap_count = max(overlaps_and_counts, key=lambda x:x[1])
        proposed_facet_count = dfs[decoder[proposed_new_facet]]
        # TODO

    append = True # insert the facet after the check. assume true

    for index, facet in enumerate(output): # loop over facets thus far
        dist = distance(facet, proposed_new_facet) # get lev distance
        if dist > 0 and dist < 3: # if lev. distance is less than 2
            # if the proposed facet is longer than the good one
            # the [-1:] below prevents replacing "Mitch Landrieu" w/ "Mitch Landrieus"
            if s_check(facet, proposed_new_facet, dist):
                append = False
            elif (len(proposed_new_facet) > len(facet)):
                debug_print("replacing {} with {}".format(output[index], proposed_new_facet))
                output[index] = proposed_new_facet
                append = False
        if get_jaccard(proposed_new_facet, facet) > .5:
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

    return output #sometimes more than 1 facet will be replaced by propsed_new_facet


def get_all_facets(raws, structures, q):
    '''
    :param structures: data structures for facets
    :param facet_type: could be people/ngram/org but will always = ngram basically
    :param q: query
    :return:
    '''
    output = []
    for possible_f in raws:
        output = heuristic_cleanup(output, possible_f[0], structures, q)
    return output


def get_facet_tfidf_cutoff(results, structures, facet_type):
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
    sorted_x = sorted(tfidfs.items(), key=operator.itemgetter(1), reverse=True)[0:CUTOFF]
    return [(structures["reverse_decoders"][facet_type][int(i[0])], i[1]) for i in sorted_x] # i[0] is ngram, i[1] is tfidf score


def get_raw_facets(results, bins, structures):
    '''
    Returns top_n facets per bin + top_n for global bin
    '''
    return get_facet_tfidf_cutoff(results, structures, "ngram")


def get_facets_for_q(q, results, n_facets, structures):
    '''
    Provide q, set of results and n_facets. 

    Return binned facets. TODO: xrange(2010, 2016) hardcodes bins for now 
    '''

    facet_results = defaultdict(list) # results per bin. output.

    if len(results) == 0:
        return facet_results

    min_yr = min(structures["pubdates"][int(r)].year for r in results)
    max_yr = max(structures["pubdates"][int(r)].year for r in results)

    # tf and idf score + string -- no filtering heutistics
    raw_facets = get_raw_facets(results, xrange(min_yr, max_yr), structures)

    # run a filtering heuristic to clean up facets
    ok_facets = get_all_facets(raw_facets, structures, q)

    # find the ok_facets in the raw_facets
    filtered_facets = [i for i in raw_facets if i[0] in ok_facets]

    # return the strings, in order of i
    return {"g": [i[0] for i in filtered_facets]}

if __name__ == '__main__':

    from webapp.models import query
    parser = argparse.ArgumentParser(description='parser')
    parser.add_argument("-v", action="store_true", default=False, help="verbose")
    parser.add_argument('-q', '--query', dest='query')
    parser.add_argument('-c', '--corpus', dest='corpus')
    args = parser.parse_args()

    if args.v:
        DEBUG = True
    else:
        DEBUG = False

    CORPUS = args.corpus
    NDOCS = get_ndocs(CORPUS)

    STOPTOKENS = ["new", "orleans", "york"]

    aliases = defaultdict(list)

    DEBUG = False # by default false. can be set to T w/ arg -v in command line mode

    CORPUS_ID = getcorpusid(CORPUS)
    RESULTZ = query(args.query, args.corpus)
    structures = load_all_data_structures(CORPUS)
    startTime = time.time()
    facets = get_facets_for_q(args.query, RESULTZ, 9, structures)

session.close()