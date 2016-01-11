'''
Queries whoosh and builds facets for query
'''
from experiment.models import ROOKIE
from pylru import lrudecorator
import ujson
import numpy as np
import ipdb
import time
import itertools
import cPickle as pickle
import redis

results = ROOKIE.query("Mitch Landrieu")

people_key = pickle.load(open("rookieindex/people_key.p", "rb"))
people_key_r = {v: k for k, v in people_key.items()}


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

def load_matrix(name):
    print name
    add_to_redis(name, pickle.load(open("rookieindex/{}.p".format(name), "rb")))

for n in ["people_matrix", "org_matrix", "ngram_matrix"]:
    load_matrix(n)

add_to_redis("p", people_matrix)
# newww = get_from_redis("p", people_matrix.shape[0], people_matrix.shape[1])

# print np.array_equal(people_matrix, newww)
# print people_matrix[ np.ix_([i for i in range(people_matrix.shape[0])],[int(i) for i in results])]