'''
Queries whoosh and builds facets for query
'''
from __future__ import division
from experiment.models import ROOKIE
from pylru import lrudecorator
from whoosh import query
from dateutil.parser import parse
from whoosh.index import open_dir
import ujson
import numpy as np
import ipdb
import time
import itertools
import cPickle as pickle
import redis
import sys
from Levenshtein import distance

stops = ["the lens", "new orleans", "staff writer", "orleans parish"]

NDOCS = 3488  # how many docs are indexed in whoosh?

STOPTOKENS = ["new", "orleans"]

DEBUG = True

Q = sys.argv[1]

def debug_print(msg):
    if DEBUG:
        print msg

def add_to_redis(key, value):
    '''
    Value is a multi dimensional numpy array.
    It is flattened in row major order and stored in redis
    #http://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.matrix.flatten.html
    This is b/c redis will store as string instead of as np array
    '''
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set(key, value.flatten().tobytes())


def get_from_redis(key, row, col):
    '''
    Restores an array stored in redis as bytes.
    need to supply how many rows/cols in the original matrix
    '''
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    s = r.get(key)
    deserialized = np.frombuffer(s).astype(np.float64)
    rebuilt = deserialized.reshape((row, col))
    return rebuilt

def load_matrix(key, row, col):
    '''
    loads a F x D matrix (via redis)
    '''
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    if r.get(key) is None:
        print "[*] Hang on. Adding {} to redis".format(name)
        add_to_redis(key, pickle.load(open("rookieindex/{}.p".format(name), "rb")))
    return get_from_redis(key, row, col)

@lrudecorator(100)
def get_metadata_file():
    t0=time.time()
    with open("rookieindex/meta_data.json") as inf:
        metadata = ujson.load(inf)
    return metadata

def load_all_data_structures():
    '''
    Load everything indexed in build_matrix.py
    '''
    decoders = {}
    reverse_decoders = {}
    matrixes = {}
    df = {}
    idf = {}
    mt = get_metadata_file()
    for n in ["people", "org", "ngram"]:
        decoder = pickle.load(open("rookieindex/{}_key.p".format(n), "rb"))
        decoder_r = {v: k for k, v in decoder.items()}
        decoders[n] = decoder
        reverse_decoders[n] = decoder_r
        matrixes[n] = load_matrix(n + "_matrix", len(decoder.keys()), NDOCS)
        df[n] = pickle.load(open("rookieindex/{}_df.p".format(n), "rb"))
        idf[n] = pickle.load(open("rookieindex/{}_idf.p".format(n), "rb"))
    return {"decoders": decoders, "reverse_decoders": reverse_decoders, "matrixes": matrixes, "df": df, "idf": idf, "metadata": mt}


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


def heuristic_cleanup(output, proposed_new_facet):
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
    if proposed_new_facet.lower() in stops:
        return output # dont and the new facet
    if proposed_new_facet in output:
        return output # dont add duplicates
    if get_jaccard(proposed_new_facet, Q) > .5:
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


    if append:
        debug_print("appending {}".format(proposed_new_facet))
        output.append(proposed_new_facet)
    return [i for i in set(output)] #sometimes more than 1 facet will be replaced by propsed_new_facet

def get_facets(results, structures, facet_type, num_facets):
    '''
    get the tfidf score for each facet_type
    '''
    start = time.time()
    tfidf = get_facet_tfidf(results, structures, facet_type)
    output = []
    for ii in np.argsort(tfidf)[::-1]:
        possible_f = structures["reverse_decoders"][facet_type][ii]
        output = heuristic_cleanup(output, possible_f)
        #output = output + [possible_f]
        if len(output) == num_facets:
            break
    debug_print("getting facets took {}".format(time.time() - start))
    return output


def get_facet_tfidf(results, structures, facet_type):
    '''
    get the tfidf score for each facet_type
    "tf" = how many queried documents contain f (i.e. boolean: facet occurs or no)
    "df" = how many total documents contain f (i.e. boolean: facet occurs or no)
    "tfidf" = np.multiply(tf, np.log(1./df))
    '''
    start = time.time()
    # this is the bottle neck --> 
    cols = structures["matrixes"][facet_type][ np.ix_([i for i in range(structures["matrixes"][facet_type].shape[0])],[int(i) for i in results])]
    debug_print("getting cols index took {}".format(time.time() - start))
    tf = np.sum(cols, axis=1) # occurance in queried docs, by F
    idf = structures["idf"][facet_type]
    tfidf = np.multiply(tf, idf)
    return tfidf

def filter_t(results, start, end):
    '''
    Take a set of results and return those that fall in [start, end]
    '''
    return [i for i in results if parse(structures["metadata"][i]["pubdate"]) >= start and parse(structures["metadata"][i]["pubdate"]) <= end]

structures = load_all_data_structures()
results = set(ROOKIE.query(Q))
start = time.time()
results = filter_t(results, parse("2012-01-01"), parse("2013-01-01"))
debug_print("filter t took {}".format(time.time() - start))
print get_facets(results, structures, "ngram", 15)
