'''
This module loads a facet_document matrix
'''
from rookie.classes import IncomingFile
from collections import defaultdict
from pylru import lrudecorator
import ujson
import os
import ipdb
import glob
import time
import ipdb
import cPickle as pickle
import numpy as np

from whoosh import query
from whoosh.index import open_dir


def get_all_doc_ids():
    index = open_dir("rookieindex")
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
    with open("rookieindex/meta_data.json") as inf:
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
            if counter % 100 == 0:
                print counter
            print MT[docid].keys()
            people = MT[docid]["people"]
            org = MT[docid]["org"]
            ngram = MT[docid]["ngram"]
            for p in people:
                people_count[p] += 1
            for o in org:
                org_count[o] += 1
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

    # dict to look up correct row #s in array
    person_to_slot = {p: i for (i, p) in enumerate(ok_people)}
    org_to_slot = {o: i for (i, o) in enumerate(ok_org)}
    ngram_to_slot = {n: i for (i, n) in enumerate(ok_ngrams)}

    pickle.dump(person_to_slot, open("rookieindex/people_key.p", "wb" ))
    pickle.dump(org_to_slot, open("rookieindex/org_key.p", "wb" ))
    pickle.dump(ngram_to_slot, open("rookieindex/ngram_key.p", "wb" ))

    people_matrix = np.zeros((len(ok_people), len(docids)))
    org_matrix = np.zeros((len(ok_org), len(docids)))
    ngram_matrix = np.zeros((len(ok_ngrams), len(docids)))

    people_counter = defaultdict(int)
    ngram_counter = defaultdict(int)
    org_counter = defaultdict(int)

    for dinex, docid in enumerate(docids):
        print dinex
        people = set([str(i) for i in MT[unicode(docid)]["people"] if str(i) in ok_people])
        org = set([str(i) for i in MT[unicode(docid)]["org"]  if str(i) in ok_org])
        ngram = set([str(j) for j in MT[unicode(docid)]["ngram"] if j in ok_ngrams])
        docid = int(docid)
        for p in people:
            people_matrix[person_to_slot[p]][docid] = 1
            people_counter[p] += 1
        for o in org:
            org_matrix[org_to_slot[o]][docid] = 1
            org_counter[o] += 1
        for n in ngram:
            ngram_matrix[ngram_to_slot[n]][docid] = 1
            ngram_counter[n] += 1

    pickle.dump(df_vec(people_counter, person_to_slot, len(ok_people)), open("rookieindex/people_df.p", "wb" ))
    pickle.dump(df_vec(org_counter, org_to_slot, len(ok_org)), open("rookieindex/org_df.p", "wb" ))
    pickle.dump(df_vec(ngram_counter, ngram_to_slot, len(ok_ngrams)), open("rookieindex/ngram_df.p", "wb" ))
    
    NDOCS = len(docids)
    #np.log(NDOCS / df)
    pickle.dump(np.log(NDOCS / df_vec(people_counter, person_to_slot, len(ok_people))), open("rookieindex/people_idf.p", "wb" ))
    pickle.dump(np.log(NDOCS / df_vec(org_counter, org_to_slot, len(ok_org))), open("rookieindex/org_idf.p", "wb" ))
    pickle.dump(np.log(NDOCS / df_vec(ngram_counter, ngram_to_slot, len(ok_ngrams))), open("rookieindex/ngram_idf.p", "wb" ))
    
    pickle.dump(people_matrix, open("rookieindex/people_matrix.p", "wb" ))
    pickle.dump(org_matrix, open("rookieindex/org_matrix.p", "wb" ))
    pickle.dump(ngram_matrix, open("rookieindex/ngram_matrix.p", "wb" ))


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

