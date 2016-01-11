'''
Queries whoosh and builds facets for query
'''
from experiment.models import ROOKIE
from pylru import lrudecorator
from whoosh import query
from whoosh.index import open_dir
import ujson
import numpy as np
import ipdb
import time
import math
import itertools
import cPickle as pickle
import redis
from Levenshtein import distance

stops = ["the lens", "new orleans", "staff writer"]

NDOCS = 3488  # how many docs are indexed in whoosh?

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

def load_all_data_structures():
    '''
    Load everything indexed in build_matrix.py
    '''
    decoders = {}
    reverse_decoders = {}
    matrixes = {}
    df = {}
    for n in ["people", "org", "ngram"]:
        decoder = pickle.load(open("rookieindex/{}_key.p".format(n), "rb"))
        decoder_r = {v: k for k, v in decoder.items()}
        decoders[n] = decoder
        reverse_decoders[n] = decoder_r
        matrixes[n] = load_matrix(n + "_matrix", len(decoder.keys()), NDOCS)
        df[n] = pickle.load(open("rookieindex/{}_df.p".format(n), "rb"))
    return {"decoders": decoders, "reverse_decoders": reverse_decoders, "matrixes": matrixes, "df": df}


def s_check(facet, proposed_new_facet, distance):
    '''
    For cases like "Mitch Landrieu vs. Mitch Landrieus"
    '''
    if distance != 1:
        return False
    if proposed_new_facet[-1:] == "s" and facet[-1:] != "s":
        return True
    return False


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
    if proposed_new_facet.lower() in stops:
        return output # dont and the new facet
    insert = True # insert the facet after the check. assume true
    for index, facet in enumerate(output): # loop over facets thus far
        dist = distance(facet, proposed_new_facet) # get lev distance
        if dist > 0 and dist < 3: # if lev. distance is less than 2
            # if the proposed facet is longer than the good one
            # the [-1:] below prevents replacing "Mitch Landrieu" w/ "Mitch Landrieus"
            if s_check(facet, proposed_new_facet, dist):
                insert = False
            elif (len(proposed_new_facet) > len(facet)):
                print "replacing {} with {}".format(output[index], proposed_new_facet)
                output[index] = proposed_new_facet
                insert = False

    if insert:
        output.append(proposed_new_facet)
    return output

def get_facets(results, structures, facet_type, num_facets):
    '''
    get the tfidf score for each facet_type
    "tf" = how many queried documents contain f (i.e. boolean: facet occurs or no)
    "df" = how many total documents contain f (i.e. boolean: facet occurs or no)
    "tfidf" = np.multiply(tf, 1./df)
    '''
    start = time.time()
    tfidf = get_facet_tfidf(results, structures, facet_type)
    decoded = [(structures["reverse_decoders"][facet_type][i], v) for i, v in enumerate(tfidf)]
    decoded.sort(key=lambda x: x[1], reverse=True)
    output = []
    for possible_f in decoded:
        output = heuristic_cleanup(output, possible_f[0])
        if len(output) == num_facets:
            break

    end = time.time()
    print "finding facets took {}".format(end - start)
    return output


def get_facet_tfidf(results, structures, facet_type):
    '''
    get the tfidf score for each facet_type
    "tf" = how many queried documents contain f (i.e. boolean: facet occurs or no)
    "df" = how many total documents contain f (i.e. boolean: facet occurs or no)
    "tfidf" = np.multiply(tf, np.log(1./df))
    '''
    cols = structures["matrixes"][facet_type][ np.ix_([i for i in range(structures["matrixes"][facet_type].shape[0])],[int(i) for i in results])]
    tf = np.sum(cols, axis=1) # occurance in queried docs, by F
    df = structures["df"][facet_type]
    idf = np.log(NDOCS / df)
    tfidf = np.multiply(tf, idf)
    return tfidf

structures = load_all_data_structures()
results = ROOKIE.query("Mitch Landrieu")
print get_facets(results, structures, "ngram", 9)

