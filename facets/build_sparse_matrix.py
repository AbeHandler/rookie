'''
Create a sparse matrix for every doc showing what ngrams it has.

These should be very small b.c gonna try to fit them all in memory
'''
from webapp.classes import IncomingFile
from collections import defaultdict
from pylru import lrudecorator
from joblib import Memory
from tempfile import mkdtemp
import ujson
import datetime
import os
import ipdb
import glob
import sys
import time
import ipdb
import cPickle as pickle
import numpy as np
import joblib
import argparse
from webapp.models import get_doc_metadata
from whoosh import query
from whoosh.index import open_dir

from dateutil.parser import parse

parser = argparse.ArgumentParser()
parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
args = parser.parse_args()

cachedir = mkdtemp()
memory = Memory(cachedir=cachedir, verbose=1)

'''build connection to db'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp.classes import CONNECTION_STRING
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()


def getcorpusid():
    go = lambda *args: session.connection().execute(*args)
    for i in go("select corpusid from corpora where corpusname='{}'".format(args.corpus)):
        return i[0]

CORPUSID = getcorpusid()

def get_all_doc_ids():
    index = open_dir("indexes/{}/".format(args.corpus))
    qr = query.Every()
    with index.searcher() as srch:
        results_a = srch.search(qr, limit=None)
        out = [a.get("path").replace("/", "") for a in results_a]
        return out

# get all docids from whoosh
ALLDOCIDS = get_all_doc_ids()

def count_facets():
    '''
    This function counts every person, org and ngram in the corpus
    '''
    ngram_count = defaultdict(int)

    counter = 0
    print "looping over all docis to count ngrams"

    for docid in ALLDOCIDS:
        try:
            counter += 1
            if counter % 1000 == 0:
                sys.stdout.write("...%s" % counter); sys.stdout.flush()
            ngram = get_doc_metadata(docid)["ngrams"]
            for n in ngram:
                ngram_count[n] += 1        

        except UnicodeError:
            print "error"

    return ngram_count


def df_vec(counter, decoder, noccurs):
    '''
    counter tracks how many times an F occurs in all docs
    decoder translates from an F to a row in a F X D matrix
    noccurs = how may total F of a given type
    '''
    df_out = np.zeros(noccurs)
    for c in counter:
        # i.e. in the row corresponding to c (ex. landrieu) set val to df
        df_out[decoder[c]] = counter[c]
    return df_out

def build_matrix(docids, ok_ngrams):
    '''
    This function builds sparse count vectors for each doc, held in memory
    '''
    print "[*] Building sparse vectors, putting them in postgres ... "

    string_to_pubdate_index = defaultdict(list)

    go = lambda *args: session.connection().execute(*args)
    # dict to look up correct row #s in array
    ngram_to_slot = {n: i for (i, n) in enumerate(ok_ngrams)}

    pickle.dump(ngram_to_slot, open("indexes/{}/ngram_key.p".format(args.corpus), "wb" ))

    ngram_counter = defaultdict(int)

    pubdates = {}

    for dinex, docid in enumerate(docids):
        if dinex % 1000 == 0:
            sys.stdout.write("...%s" % dinex); sys.stdout.flush()
        pubdate = datetime.datetime.strptime(get_doc_metadata(docid)["pubdate"], '%Y-%m-%d')
        pubdates[docid] = pubdate
        ngram = set([str(j) for j in get_doc_metadata(docid)["ngrams"] if j in ok_ngrams])
        docid = int(docid)
        ngrams_in_doc = {}
        for n in ngram:
            ngrams_in_doc[ngram_to_slot[n]] = 1
            string_to_pubdate_index[n].append(get_doc_metadata(docid)["pubdate"])
            ngram_counter[n] += 1
        go("""INSERT INTO count_vectors (docid, CORPUSID, data) VALUES (%s, %s, %s)""", dinex, int(CORPUSID), ujson.dumps(ngrams_in_doc))
    session.commit()
    print "\ndumping pickled stuff..."

    NDOCS = len(docids)

    pickle.dump(pubdates, open("indexes/{}/pubdates_xpress.p".format(args.corpus), "wb" ))

    pickle.dump(df_vec(ngram_counter, ngram_to_slot, len(ok_ngrams)), open("indexes/{}/ngram_df.p".format(args.corpus), "wb" ))

    pickle.dump(np.log(NDOCS / df_vec(ngram_counter, ngram_to_slot, len(ok_ngrams))), open("indexes/{}/ngram_idf.p".format(args.corpus), "wb" ))
    
    pickle.dump(dict(string_to_pubdate_index), open("indexes/{}/string_to_pubdate_index.p".format(args.corpus), "wb" ))


def filter(input, n):
    '''
    Filter input to cases where v > n
    '''
    return set([str(k) for k, v in input.iteritems() if v >= n])


if __name__ == '__main__':
    all_facets = count_facets()
    options = [1, 5,10,15,20,25]
    print ""
    for n in options:
        ngram = filter(all_facets, n)
        print "Found {} ngrams with a filter of {}".format(len(ngram), n)
    build_matrix(ALLDOCIDS, filter(all_facets, 10))
