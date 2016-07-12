'''
CVB0 + Daume for Rookie

Daume note: J fixed at 1

Queries: boolean for now

To-try: supervision for F, like in dict classifier

'''

from __future__ import division
from collections import defaultdict
from ctypes import c_int
from numpy.ctypeslib import as_ctypes
import argparse
import cPickle as pickle
import ctypes
import sys
import string
import ujson as json
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-corpus", type=str, help="corpus")
ARGS = parser.parse_args()


from stop_words import get_stop_words
# os.system("./make.sh")

# To ignore numpy errors in pylint:
# pylint: disable=E1101

GLM_K = 0
QLM_K = 1

query = ["jail", "consent", "decree", "gusman"]

## set up model.  
class Model:
    pass

## token level data
class Dataset:
    pass


def run_sweep(dd, mm, starttok, endtok):
    '''update tok range'''
    # python for now. should be written in a way that makes it be easy to xfer to C

    alpha = .5  # simple uniform priors for now
    eta = .5
    for i in range(starttok, endtok):

        np.subtract(mm.N_k, mm.Q_ik[i], out=mm.N_k)
        np.subtract(mm.N_wk[dd.i_w[i]], mm.Q_ik[i], out=mm.N_wk[dd.i_w[i]])
        np.subtract(mm.N_sk[dd.i_s[i]], mm.Q_ik[i], out=mm.N_sk[dd.i_s[i]])

        # assert np.where(mm.N_k < 0)[0].shape[0] == 0
        # assert np.where(mm.N_wk < 0)[0].shape[0] == 0
        # assert np.where(mm.N_sk < 0)[0].shape[0] == 0

        ks = (mm.N_wk[dd.i_w[i]] + eta)/(mm.N_k + (dd.V * eta)) * (mm.N_sk[dd.i_s[i]])
        ks = ks / np.sum(ks)

        mm.Q_ik[i] = ks
        np.add(mm.N_k, ks, out=mm.N_k)
        np.add(mm.N_wk[dd.i_w[i]], ks, out=mm.N_wk[dd.i_w[i]])
        np.add(mm.N_sk[dd.i_s[i]], ks, out=mm.N_sk[dd.i_s[i]])


SW = get_stop_words('en') + ["city", "new", "orleans", "lens", "report", "said", "-lrb-", "-rrb-", "week"]
SW = SW + [o for o in string.punctuation]

libc = ctypes.CDLL("./cvb0.so")


def fill_emprical_language_models(dd, mm):
    '''find p(W|K) for each doc, G and Q lm'''
    smoothing = 1
    mm.emprical_N_wk = np.zeros((K,V), dtype=np.float32)
    print "\t - Adding up the empirical language model\n"
    for k in range(K):
        if k % 100 == 0:
            sys.stderr.write("{} of {}\t".format(k, K))
        tot_words = sum(dd.doc_counts[k]) + (smoothing * V)
        for v in range(V):
            try:
                tot_word = tot_word = dd.doc_counts[k][v] + smoothing
            except KeyError:  # i.e. word does not appear
                tot_word = smoothing
            mm.emprical_N_wk[k][v] = tot_word/tot_words
    print "\t Done"


def default_to_regular(d):
    '''convert default dict to regular'''
    # stackoverflow: default dict to regular
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.iteritems()}
    return d


def build_dataset():
    ## load data.  will be faster to pre-numberize it.

    # docids are offset by 2. First 2 "docids" are reserved for global and query lm
    print "[*] Building dataset"
    word2num = {}
    num2word = []
    dd = Dataset()
    dd.docids = []
    dd.tokens = []  ## wordids
    wordcount = defaultdict(int)

    sentences = 0

    # emprical language model, for initialization
    doc_counts = defaultdict(lambda: defaultdict(int))
    hits = [] # stores vector of positive or negative: matches query?
    i_s = [] # maps i -> sentence
    i_w = [] # maps i -> w
    D_ = 0
    i_dk = [] # maps i -> dk
    s_i = defaultdict(list)
    i = 0
    for docid,line in enumerate(open("lens.anno")):
        if docid > 25: break 
        doc = json.loads(line)["text"]
        hit = 0
        for s_ix, sent in enumerate(doc['sentences']):
            reals = [word for word in sent["tokens"] if word.lower() not in SW]
            s_i[sentences] = []
            for word in reals:
                
                i_s.append(sentences) # building a vector of sentences for each token, i
                i_dk.append(docid + 2)
                word = word.lower()
                if word in query:
                    hit = 1
                wordcount[word] += 1
                if word not in word2num:
                    n = len(word2num)
                    word2num[word] = n
                    num2word.append(word)
                    assert num2word[n] == word
                else:
                    n = word2num[word]
                doc_counts[docid + 2][n] += 1
                doc_counts[GLM_K][n] += 1
                doc_counts[QLM_K][n] = 0
                dd.tokens.append(n)
                i_w.append(n)
                s_i[sentences].append(i)
                i += 1
            dd.docids.append(docid + 2)
            sentences += 1
        # have to loop 2x here b/c need to see if doc is a hit first
        for s_ix, sent in enumerate(doc['sentences']): 
            reals = [word for word in sent["tokens"] if word.lower() not in SW]
            for w in reals:
                hits.append(hit)

        D_ += 1

    # an I length vector mapping i->hit. hit = i's document matches query
    dd.hits = np.array(hits, dtype=np.uint32)
    dd.S = sentences
    dd.i_dk = i_dk
    dd.i_w = np.array(i_w, dtype=np.uint32) # i->w
    dd.i_s = np.array(i_s, dtype=np.uint32) # i->s
    dd.s_i = dict(s_i)
    assert dd.i_w.shape[0] == dd.i_s.shape[0]
    # a S length vector w/ the doc id for each S
    dd.docids = np.array(dd.docids, dtype=np.uint32) 
    dd.tokens = np.array(dd.tokens, dtype=np.uint32)
    dd.D = D_ # cant look at end of array b/c is 2 extra
    dd.V = len(word2num)
    dd.Ntok = len(dd.tokens)
    dd.doc_counts = default_to_regular(doc_counts)
    dd.word2num = word2num
    dd.num2word = num2word
    pickle.dump(dd, open(ARGS.corpus + ".dd", "wb"))
    print "[*] Built dataset"
    return dd


try:
    dd = pickle.load(open(ARGS.corpus + ".dd", "rb"))
    print "[*] Found & loaded cached dataset"
except IOError:
    print "[*] Could not find cached dataset. Building one"
    dd = build_dataset()

K = dd.D + 1 + 1 # i.e. D language models, plus a Q model, plus a G model
# for any given Q_i, only 3 of these will be relevant
V = len(dd.word2num)
D = dd.D
S = dd.S
Ntok = len(dd.tokens)


def make_model():
    '''set up the model'''
    mm = Model()
    mm.Q_ik = np.zeros((Ntok,K), dtype=np.float32)
    mm.N_k = np.zeros(K, dtype=np.float32)
    mm.N_sk = np.zeros((S,K), dtype=np.float32)
    mm.N_wk = np.zeros((V,K), dtype=np.float32)
    mm.N_w = np.zeros(V, dtype=np.float32)

    ## counting pass could be expensive
    for ww in dd.tokens:
        mm.N_w[ww] += 1     

    ## priors
    mm.E_wk = 1.0/V * np.ones((V,K), dtype=np.float32)
    mm.E_k  = mm.E_wk.sum(0)
    mm.A_sk = 1.0/K * np.ones((S,K), dtype=np.float32)
    return mm

def fill_qi_and_count(dd, mm):
    '''init w/ emprical language models from D and G'''
    # if a doc is not responsive to a query, there are only 2 options for the token: D or G
    # if it is responsive to query, there are 3 options  
    print "[*] Filling Q_i and counting ntok={}".format(Ntok)
    print "\t - Filling Q_ik"
    ks = np.zeros(K)
    nsk = np.zeros((S, K))
    nwk = np.zeros((V, K))
    for i_ in range(Ntok):
        w = dd.i_w[i_]
        mm.Q_ik[i_][GLM_K] = mm.emprical_N_wk[GLM_K][w]
        if dd.hits[i_] == 1:
            mm.Q_ik[i_][QLM_K] = mm.emprical_N_wk[GLM_K][w] * 2 # init query lm to global X 2 ? 
        dk = dd.i_dk[i_] # i's document lm
        mm.Q_ik[i_][dk] = mm.emprical_N_wk[dk][w]
        mm.Q_ik[i_] = mm.Q_ik[i_]/np.sum(mm.Q_ik[i_]) # normalize
        np.add(ks, mm.Q_ik[i_], out=ks)
        np.add(nsk[dd.i_s[i_]], mm.Q_ik[i_], out=nsk[dd.i_s[i_]])
        np.add(nwk[dd.i_w[i_]], mm.Q_ik[i_], out=nwk[dd.i_w[i_]])
        assert round(np.sum(mm.Q_ik[i_]), 5) == 1.
        assert np.where(mm.Q_ik[i_] != 0)[0].shape[0] <= 3 # no more than 3 ks turned on per row

    print "\t - Counting N_k, N_wk and N_sk".format(Ntok)

    mm.N_k = ks
    mm.N_sk = nsk
    mm.nwk = nwk


try:
    mm = Model()
    # annoying that all this stuff is serialized individually.
    # but pickle was freezing on Q_ik: https://github.com/numpy/numpy/issues/2396
    mm.N_k = np.load(ARGS.corpus + ".N_k.dat")  
    mm.N_wk = np.load(ARGS.corpus + ".N_wk.dat")
    mm.N_sk = np.load(ARGS.corpus + ".N_sk.dat")
    mm.Q_ik = np.load(ARGS.corpus + ".Q_ik.gz")
    print "[*] Found & loaded cached model"
except IOError:
    print "[*] Could not find cached model. Building one"
    mm = make_model()
    fill_emprical_language_models(dd, mm)
    fill_qi_and_count(dd, mm)
    print "[*] Dumping model"
    mm.N_k.dump(ARGS.corpus + ".N_k.dat")
    mm.N_wk.dump(ARGS.corpus + ".N_wk.dat")
    mm.N_sk.dump(ARGS.corpus + ".N_sk.dat")

    # https://github.com/numpy/numpy/issues/2396
    # using np.savetxt for big matrixes b/c 
    # apparently pickle does not work for that until python 3.3
    np.savetxt(ARGS.corpus + ".Q_ik.gz", mm.Q_ik)


print "[*] Prelims complete"
for itr in range(100):
    # print loglik(dd, mm)
    run_sweep(dd,mm, 0,len(dd.tokens))
    print "=== Iter",itr


for i in np.argsort(mm.N_wk[QLM_K])[-5:]:
    print dd.num2word[i]
