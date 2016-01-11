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
import itertools
import cPickle as pickle
import redis

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
    for n in ["people", "org", "ngram"]:
        decoder = pickle.load(open("rookieindex/{}_key.p".format(n), "rb"))
        decoder_r = {v: k for k, v in decoder.items()}
        decoders[n] = decoder
        reverse_decoders[n] = decoder_r
        matrixes[n] = load_matrix(n + "_matrix", len(decoder.keys()), NDOCS)
    return {"decoders": decoders, "reverse_decoders": reverse_decoders, "matrixes": matrixes}

def get_facets(results, structures, facet_type):
    t0=time.time()
    cols = structures["matrixes"][facet_type][ np.ix_([i for i in range(structures["matrixes"][facet_type].shape[0])],[int(i) for i in results])]
    perfacet = [(structures["reverse_decoders"][facet_type][i],v) for i,v in enumerate(np.sum(cols, axis=1))]
    perfacet.sort(key=lambda x:x[1])
    print "Got facets in {} secs".format(time.time()-t0)
    return perfacet

structures = load_all_data_structures()
results = ROOKIE.query("Mitch Landrieu")
get_facets(results, structures, "ngram")

