'''
This module loads a facet_document matrix
'''
from webapp.classes import IncomingFile
from collections import defaultdict
from pylru import lrudecorator
from joblib import Memory
from tempfile import mkdtemp
import ujson
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
from whoosh import query
from whoosh.index import open_dir

from dateutil.parser import parse

parser = argparse.ArgumentParser()
parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
args = parser.parse_args()

cachedir = mkdtemp()
memory = Memory(cachedir=cachedir, verbose=1)

def get_all_doc_ids():
    index = open_dir("indexes/{}/".format(args.corpus))
    qr = query.Every()
    with index.searcher() as srch:
        results_a = srch.search(qr, limit=None)
        out = [a.get("path").replace("/", "") for a in results_a]
        return out

# get all docids from whoosh
ALLDOCIDS = get_all_doc_ids()

@lrudecorator(100)
def get_metadata_file():
    print "Loading metadata file"
    t0=time.time()
    with open("indexes/{}/meta_data.json".format(args.corpus)) as inf:
        metadata = ujson.load(inf)
    print "Loaded metadata file in secs:", time.time()-t0
    return metadata

MT = get_metadata_file()

def count_facets():
    '''
    This function counts every person, org and ngram in the corpus
    '''
    people_count = defaultdict(int)
    org_count = defaultdict(int)
    ngram_count = defaultdict(int)

    counter = 0

    for docid in ALLDOCIDS:
        try:
            counter += 1
            if counter % 1000 == 0:
                sys.stdout.write("...%s" % counter); sys.stdout.flush()
            ngram = MT[docid]["ngrams"]
            for n in ngram:
                ngram_count[n] += 1        

        except UnicodeError:
            print "error"

    return people_count, org_count, ngram_count


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

def build_matrix(docids, ok_people, ok_org, ok_ngrams):
    '''
    This function builds three facet X doc matrixes: one for people, one for org, one for ngrams
    '''
    print "[*] Building three facet X doc matrixes"

    string_to_pubdate_index = defaultdict(list)

    # dict to look up correct row #s in array
    ngram_to_slot = {n: i for (i, n) in enumerate(ok_ngrams)}

    pickle.dump(ngram_to_slot, open("indexes/{}/ngram_key.p".format(args.corpus), "wb" ))

    ngram_matrix = np.zeros((len(ok_ngrams), len(docids)))

    ngram_counter = defaultdict(int)

    for dinex, docid in enumerate(docids):
        if dinex % 1000 == 0:
            sys.stdout.write("...%s" % dinex); sys.stdout.flush()
        ngram = set([str(j) for j in MT[unicode(docid)]["ngrams"] if j in ok_ngrams])
        docid = int(docid)
        for n in ngram:
            ngram_matrix[ngram_to_slot[n]][docid] = 1
            string_to_pubdate_index[n].append(MT[unicode(docid)]["pubdate"])
            ngram_counter[n] += 1

    pickle.dump(df_vec(ngram_counter, ngram_to_slot, len(ok_ngrams)), open("indexes/{}/ngram_df.p".format(args.corpus), "wb" ))
    
    NDOCS = len(docids)

    print "\ndumping pickled stuff..."
    pickle.dump(np.log(NDOCS / df_vec(ngram_counter, ngram_to_slot, len(ok_ngrams))), open("indexes/{}/ngram_idf.p".format(args.corpus), "wb" ))
    
    joblib.dump(ngram_matrix, 'rookieindex/ngram_matrix.joblib')
    pickle.dump(dict(string_to_pubdate_index), open("indexes/{}/string_to_pubdate_index.p".format(args.corpus), "wb" ))

    '''
@memory.cache
def ngram_matrix(docids, ok_ngrams):

    This function builds three facet X doc matrixes: one for people, one for org, one for ngrams

    print "[*] Facet X doc matrixes"

    ngram_to_slot = {n: i for (i, n) in enumerate(ok_ngrams)}

    ngram_matrix = np.zeros((len(ok_ngrams), len(docids)))

    ngram_counter = defaultdict(int)

    for dinex, docid in enumerate(docids):
        ngram = set([str(j) for j in MT[unicode(docid)]["ngram"] if j in ok_ngrams])
        docid = int(docid)
        for n in ngram:
            ngram_matrix[ngram_to_slot[n]][docid] = 1
            ngram_counter[n] += 1

    return ngram_matrix
    '''

def filter(input, n):
    '''
    Filter input to cases where v > n
    '''
    return set([str(k) for k, v in input.iteritems() if v >= n])


if __name__ == '__main__':
    people, org, ngram = count_facets()
    N = 5
    people = filter(people, N)
    org = filter(org, N)
    ngram = filter(ngram, N)
    build_matrix(ALLDOCIDS, people, org, ngram)
    #print ngram_matrix(ALLDOCIDS, ngram).shape
    #print ngram_matrix(ALLDOCIDS, ngram).shape

