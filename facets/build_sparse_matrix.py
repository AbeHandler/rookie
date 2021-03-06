'''
Create a sparse matrix for every doc showing what ngrams it has.

These should be very small b.c gonna try to fit them all in memory
'''
from collections import defaultdict
from tempfile import mkdtemp
import ujson
import datetime
import os
import json
import ipdb
import glob
import sys
import time
import ipdb
from tqdm import tqdm
import pickle
import numpy as np
import argparse
from webapp.models import get_doc_metadata
from whoosh import query
from whoosh.index import open_dir

from dateutil.parser import parse

parser = argparse.ArgumentParser()
parser.add_argument('--corpus', help='the thing in the middle of corpus/{}/raw', required=True)
args = parser.parse_args()

cachedir = mkdtemp()

'''build connection to db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import CONNECTION_STRING
engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()
'''


def getcorpusid():
    with open("db/corpora_numbers.json", "r") as inf:
        dt = json.load(inf)
        assert args.corpus in dt.keys()
        return dt[args.corpus]


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

print(len(ALLDOCIDS))

def count_facets():
    '''
    This function counts every ngram in the corpus
    '''
    ngram_count = defaultdict(int)

    counter = 0
    print("looping over all docids to count ngrams")

    for docid in tqdm(ALLDOCIDS):
        try:
            counter += 1
            ngram = get_doc_metadata(str(docid), args.corpus)["ngrams"]
            for n in ngram:
                ngram_count[n] += 1

        except UnicodeError:
            print("error")

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

# http://stackoverflow.com/questions/26496831/how-to-convert-defaultdict-of-defaultdicts-of-defaultdicts-to-dict-of-dicts-o
def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d

def build_matrix(docids, ok_ngrams, all_unigrams):
    '''
    This function builds sparse count vectors for each doc, held in memory
    '''
    print("[*] Building sparse vectors, putting them in postgres ... ")

    string_to_pubdate_index = defaultdict(list)

    #go = lambda *args: session.connection().execute(*args)
    # dict to look up correct row #s in array
    ngram_to_slot = {n: i for (i, n) in enumerate(ok_ngrams)}

    unigram_to_slot = {n: i for (i, n) in enumerate(all_unigrams)}

    pickle.dump(unigram_to_slot, open("indexes/{}/unigram_key.p".format(args.corpus), "wb"))
    pickle.dump(ngram_to_slot, open("indexes/{}/ngram_key.p".format(args.corpus), "wb"))

    ngram_counter = defaultdict(int)

    pubdates = {}

    docid_n_sentences = defaultdict(int)
    urls_xpress = defaultdict(str)
    headlines_xpress = defaultdict(str)
    count_vectors = {}
    ngrams_sentences = defaultdict(lambda : defaultdict(list))
    for dinex, docid in enumerate(tqdm(docids)):
        docid = str(docid)
        mdata = get_doc_metadata(docid, args.corpus)
        pubdate = datetime.datetime.strptime(mdata["pubdate"], '%Y-%m-%d')
        pubdates[docid] = pubdate

        doc_ngrams = get_doc_metadata(docid, args.corpus)["ngrams"]
        ngram = set([j for j in doc_ngrams if j in ok_ngrams])

        urls_xpress[docid] = mdata["url"]
        headlines_xpress[docid] = mdata["headline"]
        sents = get_doc_metadata(docid, args.corpus)["sentences"]
        docid_n_sentences[docid] = get_doc_metadata(docid, args.corpus)["nsentences"]
        for s_no, sent in enumerate(sents):
            for sent_unigram in sent["tokens"]:
                try:
                    ngrams_sentences[docid][unigram_to_slot[sent_unigram]].append(s_no)
                except KeyError: # rare ngrams are not in ngram_to_slot index and so can be skipped
                    pass
        ngrams_in_doc = {}
        for n in ngram:
            ngrams_in_doc[ngram_to_slot[n]] = 1
            string_to_pubdate_index[n].append(get_doc_metadata(docid, args.corpus)["pubdate"])
            ngram_counter[n] += 1
        count_vectors[dinex] = ujson.dumps(ngrams_in_doc)
        #go("""INSERT INTO count_vectors (docid, CORPUSID, data) VALUES (%s, %s, %s)""", dinex, int(CORPUSID), ujson.dumps(ngrams_in_doc))
    #print("\ncommitting to db")
    #session.commit()

    print("\ndumping pickled stuff...")

    NDOCS = len(docids)

    pickle.dump(count_vectors, open("indexes/{}/count_vectors.p".format(args.corpus), "wb" ))

    pickle.dump(docid_n_sentences, open("indexes/{}/how_many_sents_in_doc.p".format(args.corpus), "wb" ))

    pickle.dump(urls_xpress, open("indexes/{}/urls_xpress.p".format(args.corpus), "wb" ))

    pickle.dump(pubdates, open("indexes/{}/pubdates_xpress.p".format(args.corpus), "wb" ))

    pickle.dump(headlines_xpress, open("indexes/{}/headlines_xpress.p".format(args.corpus), "wb" ))

    pickle.dump(df_vec(ngram_counter, ngram_to_slot, len(ok_ngrams)), open("indexes/{}/ngram_df.p".format(args.corpus), "wb" ))

    dfs = df_vec(ngram_counter, ngram_to_slot, len(ok_ngrams))

    ou = np.log(NDOCS / dfs)

    pickle.dump(ou, open("indexes/{}/ngram_idf.p".format(args.corpus), "wb"))

    pickle.dump(dict(string_to_pubdate_index), open("indexes/{}/string_to_pubdate_index.p".format(args.corpus), "wb" ))


def filter(input, n):
    '''
    Filter input to cases where v > n
    '''
    return set([k for k, v in input.items() if v >= n])


def get_all_unigrams(docids):
    unigrams = set()
    print("[*] looping over unigrams")
    for dinex, docid in enumerate(docids):
        for u in get_doc_metadata(docid, args.corpus)["unigrams"]:
            unigrams.add(u)
    return list(unigrams)


if __name__ == '__main__':
    all_facets = count_facets()
    ngram = filter(all_facets, 5)
    all_unigrams = get_all_unigrams(ALLDOCIDS)
    build_matrix(ALLDOCIDS, ngram, all_unigrams)
