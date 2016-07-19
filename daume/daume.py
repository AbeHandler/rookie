'''
CVB0 + Daume for Rookie

Daume note: J fixed at 1

Queries: boolean for now

To-try: supervision for F, like in dict classifier

Bugs and/or weirdness:
        ** The elbow term is not always strictly increasing. will bounce around a bit

Ideas: 
        ** could you do this in java script? 
        ** bin QLMs to get summarization for particular timespans?
        ** or make a LM for a selected range. that is sort of the dream

'''


from __future__ import division
from collections import defaultdict
from ctypes import c_int
from numpy.ctypeslib import as_ctypes
from utils import sent_to_string
import argparse
import cPickle as pickle
import datetime
from numpy.ctypeslib import as_ctypes
import ctypes as C
import ctypes
import random
import string
import ujson as json
import numpy as np
import ipdb


parser = argparse.ArgumentParser()
parser.add_argument("-corpus", type=str, help="corpus")
parser.add_argument('-NP', action='store_true', help="store NPs along w/ unigrams", default=False)
parser.add_argument('-JUSTNP', action='store_true', help="just NPs, no unigrams", default=False)
ARGS = parser.parse_args()


from stop_words import get_stop_words
# os.system("./make.sh")

# To ignore numpy errors in pylint:
# pylint: disable=E1101

GLM_K = 0
QLM_K = 1

BETA = 3  # boost query words in priors for QLM

query = ["charter", "schools"]

## set up model.
class Model:
    pass

## token level data
class Dataset:
    pass


# http://stackoverflow.com/questions/23329663/access-np-array-in-ctypes-struct
class Args(C.Structure):
    _fields_ = [("nthreads", C.c_int),
                ("starttok", C.c_int),
                ("endtok", C.c_int),
                ("tokens", C.POINTER(C.c_uint)),
                ("docids", C.POINTER(C.c_uint)),
                ("qfix", C.POINTER(C.c_uint)),
                ("K", C.c_int),
                ("V", C.c_int),
                ("A_dk", C.POINTER(C.c_float)),
                ("E_wk", C.POINTER(C.c_float)),
                ("E_k", C.POINTER(C.c_float)),
                ("Q_ik", C.POINTER(C.c_float)),
                ("N_wk", C.POINTER(C.c_float)),
                ("N_k", C.POINTER(C.c_float)),
                ("N_dk", C.POINTER(C.c_float)),
                ]

# http://stackoverflow.com/questions/17101845/python-ctypes-array-of-structs
# class Args_array(C.Structure):
#    _fields_ = [('nthread', ctypes.c_short),
#                ('all_args', ctypes.POINTER(Args))]
#
#    def __init__(self,n):
#        elems = (Args * n)()
#        self.all_args = ctypes.cast(elems, ctypes.POINTER(Args))
#        self.nthread = n


def run_sweep(dd, mm,starttok, endtok):

    assert mm.A_sk.dtype == "float64"
    assert mm.E_k.dtype == "float64"
    assert mm.E_k.dtype == "float64"
    assert mm.Q_ik.dtype == "float64"
    assert mm.N_wk.dtype == "float64"
    assert mm.N_k.dtype == "float64"
    assert mm.N_sk.dtype == "float64"
    assert np.count_nonzero(np.isnan(mm.N_k)) == 0
    assert np.count_nonzero(np.isnan(mm.N_wk)) == 0
    assert np.count_nonzero(np.isnan(mm.N_sk)) == 0
    assert len(np.where(mm.N_wk < 0)[0]) == 0
    assert len(np.where(mm.N_k < 0)[0]) == 0

    c_float_p = ctypes.POINTER(ctypes.c_float)

    args = Args()
    args.nthreads = 1
    args.starttok = starttok
    args.endtok = endtok
    args.tokens = as_ctypes(dd.tokens)
    args.docids = as_ctypes(dd.docids)
    args.qfix = as_ctypes(dd.qfix)
    args.K = dd.K
    args.V = dd.V
    args.A_dk = mm.A_sk.ctypes.data_as(c_float_p)
    args.E_wk = mm.E_wk.ctypes.data_as(c_float_p)
    args.E_k = mm.E_k.ctypes.data_as(c_float_p)
    args.Q_ik = mm.Q_ik.ctypes.data_as(c_float_p)
    args.N_wk = mm.N_wk.ctypes.data_as(c_float_p)
    args.N_k = mm.N_k.ctypes.data_as(c_float_p)
    args.N_dk = mm.N_sk.ctypes.data_as(c_float_p)

    libc.threaded_sweep(ctypes.byref(args))

    assert np.count_nonzero(np.isnan(mm.N_k)) == 0
    assert np.count_nonzero(np.isnan(mm.N_wk)) == 0
    assert np.count_nonzero(np.isnan(mm.N_sk)) == 0
    assert len(np.where(mm.N_wk < 0)[0]) == 0
    assert len(np.where(mm.N_k < 0)[0]) == 0

def run_sweep_p(dd, mm, starttok, endtok):
    '''update tok range'''
    # python for now. should be written in a way that makes it be easy to xfer to C

    if endtok != dd.Ntok:
        print "warning. not running on all tokens"
    for i in range(starttok, endtok):
        
        assert np.count_nonzero(np.isnan(mm.N_k)) == 0
        assert np.count_nonzero(np.isnan(mm.N_wk)) == 0
        assert np.count_nonzero(np.isnan(mm.N_sk)) == 0

        np.subtract(mm.N_k, mm.Q_ik[i], out=mm.N_k)
        np.subtract(mm.N_wk[dd.i_w[i]], mm.Q_ik[i], out=mm.N_wk[dd.i_w[i]])
        np.subtract(mm.N_sk[dd.i_s[i]], mm.Q_ik[i], out=mm.N_sk[dd.i_s[i]])

        assert (mm.Q_ik < 0).sum() == 0
        assert (mm.N_k < 0).sum() == 0
        assert (mm.N_wk < 0).sum() == 0
        assert (mm.N_sk < 0).sum() == 0

        ks = ((mm.N_wk[dd.i_w[i]] + mm.E_wk[dd.i_w[i]])/(mm.N_k + mm.E_k)) * (mm.A_sk[dd.i_s[i]] + mm.N_sk[dd.i_s[i]])

        assert np.where(ks != 0)[0].shape[0] <= 3

        # occassionnally have nonsense where ks is 0s b/c removed all mass in tn topic
        ks[QLM_K] = max(1e-100, ks[QLM_K]) # this avoids the NaNs.
        ks[GLM_K] = max(1e-100, ks[GLM_K])      # NOTE: ONLY 3 ks set. A dif w/ cvb0 in c
        ks[dd.i_dk[i]] = max(1e-100, ks[dd.i_dk[i]])
        ks = ks / np.sum(ks)

        assert np.where(ks != 0)[0].shape[0] <= 3
        mm.Q_ik[i] = ks
        np.add(mm.N_k, ks, out=mm.N_k)
        np.add(mm.N_wk[dd.i_w[i]], ks, out=mm.N_wk[dd.i_w[i]])
        np.add(mm.N_sk[dd.i_s[i]], ks, out=mm.N_sk[dd.i_s[i]])


SW = get_stop_words('en') + ["city", "new", "orleans", "lens", "report", "said", "-lrb-", "-rrb-", "week"]
SW = SW + [o for o in string.punctuation] + [str(o) for o in range(0, 1000)]
SW = SW + ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
SW = SW + ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
SW = SW + ["a.m.", "p.m.", "donors", "we", "cover", "be", "help", "us", "report", "feb.", "new orleans", "staff writer", "the lens"]

libc = ctypes.CDLL("./cvb0.so")



def default_to_regular(d):
    '''convert default dict to regular'''
    # stackoverflow: default dict to regular
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.iteritems()}
    return d


def toks_for_sent(sent):
    out = []
    if ARGS.JUSTNP:  # NPs only
        return [phrase["normalized"] for phrase in sent["phrases"] if len(phrase["normalized"].split()) > 1 and phrase["normalized"] not in SW]   
    if ARGS.NP:  # NPs and unigrams
        out = out + [phrase["normalized"] for phrase in sent["phrases"] if len(phrase["normalized"].split()) > 1]
    out = out + [word for word in sent["tokens"] if word.lower() not in SW]
    out  = [o for o in set(out)]
    
    return [o for o in out if o not in SW]


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

    hits = [] # stores vector of positive or negative: matches query?
    i_s = [] # maps i -> sentence
    i_w = [] # maps i -> w
    D_ = 0
    dd.i_dk = [] # maps i -> dk
    s_i = defaultdict(list)
    i = 0
    raw_sents = {}
    alpha_is = []
    tot_hits = 0

    counter = defaultdict(int)

    for docid,line in enumerate(open("lens.anno")):
        if docid > 50: break
        doc = json.loads(line)["text"]
        hit = 0
        for s_ix, sent in enumerate(doc['sentences']):
            s_i[sentences] = []
            reals = toks_for_sent(sent)
            # ipdb.set_trace()
            for word in reals:
                word = word.lower()
                i_s.append(sentences) # building a vector of sentences for each token, i
                dd.i_dk.append(docid + 2)
                counter[word] += 1
                if ARGS.JUSTNP:
                    found = False
                    for term in query:
                        if term in word: # in this case, word will be an NP w. len > 1
                            hit = 1
                    if found:
                        tot_hits += 1
                else:
                    if word in query:
                        hit = 1
                        tot_hits += 1

                wordcount[word] += 1
                if word not in word2num:
                    n = len(word2num)
                    word2num[word] = n
                    num2word.append(word)
                    assert num2word[n] == word
                else:
                    n = word2num[word]
                dd.tokens.append(n)

                i_w.append(n)
                s_i[sentences].append(i)
                i += 1
                dd.docids.append(sentences)
            raw_sents[sentences] = sent_to_string(sent)
            sentences += 1
        # have to loop 2x here b/c need to see if doc is a hit first
        for s_ix, sent in enumerate(doc['sentences']):
            reals = toks_for_sent(sent)
            for w in reals:
                hits.append(hit)

        D_ += 1

    TOT = sum(v for k,v in counter.items())
    counter_normalized = {k: v/TOT for k, v in counter.items()}

    print "total hits = {}".format(tot_hits)
    # an I length vector mapping i->hit. hit = i's document matches query
    dd.hits = np.array(hits, dtype=np.uint32)
    def invert(h_):
        return 0 if h_ is 1 else 1
    dd.qfix = np.array([invert(h) for h in hits], dtype=np.uint32)
    dd.S = sentences
    dd.i_dk = np.array(dd.i_dk, dtype=np.uint32) # i->dk
    dd.i_w = np.array(i_w, dtype=np.uint32) # i->w
    dd.i_s = np.array(i_s, dtype=np.uint32) # i->s
    dd.s_i = dict(s_i)
    # a S length vector w/ the doc id for each S
    dd.docids = np.array(dd.docids, dtype=np.uint32)
    dd.tokens = np.array(dd.tokens, dtype=np.uint32)
    dd.D = D_ # cant look at end of array b/c is 2 extra
    dd.V = len(word2num)
    dd.Ntok = len(dd.tokens)
    dd.word2num = word2num
    dd.num2word = num2word
    dd.raw_sents = raw_sents # this won't scale to corpora that dont fit in memory. TODO, maybe
    dd.K = dd.D + 1 + 1 # i.e. D language models, plus a Q model, plus a G model
    dd.glm = {word2num[k]: v for k, v in counter_normalized.items()} # empirical GLM
    pickle.dump(dd, open(ARGS.corpus + ".dd", "wb"))
    with open(ARGS.corpus + "_glm.p", "w") as outf:
        pickle.dump(dd.glm, outf)

    print "[*] Built dataset"
    return dd


try:
    dd = pickle.load(open(ARGS.corpus + ".dd", "rb"))
    print "[*] Found & loaded cached dataset"
except IOError:
    print "[*] Could not find cached dataset. Building one"
    dd = build_dataset()


# for any given Q_i, only 3 of these will be relevant
ALPHA = 1
ETA = 1.0/dd.V


def make_model(dd):
    '''set up the model'''
    print "Setting up model"
    mm = Model()
    mm.N_w = np.zeros(dd.V, dtype=np.float64)

    ## counting pass could be expensive
    for ww in dd.tokens:
        mm.N_w[ww] += 1

    ## priors
    mm.E_wk = ETA * np.ones((dd.V,dd.K), dtype=np.float64)
    for w in query:
        try:
            mm.E_wk[dd.word2num[w]][QLM_K] = BETA
        except KeyError:
            print "[*] warning: can't find query word, {} in vocab. this only makes sense if -JUSTNP is set".format(w)
            assert ARGS.JUSTNP == True
    mm.E_k  = mm.E_wk.sum(0)
    mm.A_sk = np.zeros((dd.Ntok,dd.K), dtype=np.float64)
    for i in range(dd.Ntok):
        dk = dd.i_dk[i]
        mm.A_sk[dd.i_s[i]][GLM_K] = ALPHA  # no Alpha for invalid Ks
        mm.A_sk[dd.i_s[i]][dk] = ALPHA
        if dd.hits[i] == 1:
            mm.A_sk[dd.i_s[i]][QLM_K] = ALPHA * BETA
    mm.A_sk = np.asarray(mm.A_sk, dtype=np.float64)
    mm.Q_ik = np.zeros((dd.Ntok,dd.K), dtype=np.float64) # don't pickle this part
    # just for compatibility. not used in C code.
    mm.qfix = np.zeros(dd.Ntok, dtype=np.uint32)
    return mm


def fill_and_count(dd, mm):
    '''i think its faster to let the algo converge than load empirical lm'''
    mm.N_k = np.zeros(dd.K, dtype=np.float64)
    mm.N_sk = np.zeros((dd.S, dd.K), dtype=np.float64)
    mm.N_wk = np.zeros((dd.V, dd.K), dtype=np.float64)
    print "filling dataset randomly"
    mm.Q_ik = np.zeros((dd.Ntok, dd.K), dtype=np.float64)
    assert mm.Q_ik.shape[0] == dd.Ntok
    min_ = min(v for k,v in dd.glm.items())
    max_ = max(v for k,v in dd.glm.items())

    for i_ in range(dd.Ntok):
        w = dd.i_w[i_]
        glm = dd.glm[w]
        dlm = random.uniform(min_, max_)
        if dd.hits[i_] == 1:
            qlm = random.uniform(min_, max_)
            sum_ = qlm + dlm + glm
            mm.Q_ik[i_][GLM_K] = glm/sum_
            mm.Q_ik[i_][QLM_K] = qlm/sum_
            mm.Q_ik[i_][dd.i_dk[i_]] = dlm/sum_
        else:
            sum_ = dlm + glm
            mm.Q_ik[i_][GLM_K] = glm/sum_
            mm.Q_ik[i_][dd.i_dk[i_]] = dlm/sum_
        np.add(mm.N_k, mm.Q_ik[i_], out=mm.N_k)
        np.add(mm.N_sk[dd.i_s[i_]], mm.Q_ik[i_], out=mm.N_sk[dd.i_s[i_]])
        np.add(mm.N_wk[dd.i_w[i_]], mm.Q_ik[i_], out=mm.N_wk[dd.i_w[i_]])
        assert round(np.sum(mm.Q_ik[i_]), 5) == 1.
        assert np.where(mm.Q_ik[i_] != 0)[0].shape[0] <= 3 # no more than 3 ks turned on per row



def infodot(qvec, lpvec):
    """returns sum_k q*log(p)  with q*log(p)=0 when q=0"""
    xx = qvec*lpvec
    # assert not np.isnan(np.sum(xx[qvec != 0]))
    return np.sum(xx[qvec != 0])


def loglik(dd,mm):
    ll = 0
    # should hyperparams be added in after Q sums for these? or not?

    # assert np.all(mm.N_wk > 0)
    # print "\nNum negative entries", np.sum(mm.N_wk < 0), np.min(mm.N_wk), np.sum(mm.Q_ik < 0)

    assert len(np.where(mm.N_wk < 0)[0]) == 0
    topics = mm.N_wk / mm.N_wk.sum(0)
    topics[topics <= 0] = 1e-9

    for i in xrange(len(dd.tokens)):
        w = dd.tokens[i]
        Q = mm.Q_ik[i,:]

        ## actually this is log P(w) using P(w) = sum_z Q(z)P(w|z)
        ## not sure if it's related to ELBO
        # wordprob = np.sum(topics[w,:] * Q)
        # ll += np.log(wordprob)

        ## ELBO terms
        # E[log P(w|z)]
        ll += infodot(Q, np.log(topics[w,:]))
        # E[log P(z)]: skip i'm confused. have to eval per doc dirichlets i think
        # E[log Q(z)]
        lg_q = np.log(Q)

        lg_q[np.isnan(lg_q)] = 0
        ll += infodot(Q, lg_q)
    return ll

print "total tokens {}".format(dd.Ntok)

mm = make_model(dd)

fill_and_count(dd, mm)

# pickle.dump(mm, open("lens.mm", "wb"))
#mm = pickle.load(open("lens.mm"))

print "[*] Prelims complete"

print "total tokens {}".format(dd.Ntok)
for itr in range(30):
    a = datetime.datetime.now()
    run_sweep(dd,mm,0,dd.Ntok)
    #assert len(np.where(mm.N_wk < 0)[0]) == 0
    print "\t {}".format(itr)
    # run_sweep_p(dd,mm,0,Ntok)
    assert len(np.where(mm.N_wk < 0)[0]) == 0
    assert len(np.where(mm.N_k < 0)[0]) == 0
    b = datetime.datetime.now()
    print b - a


    if itr % 10 == 0:
        print loglik(dd,mm)
        print "=== Iter",itr


def print_sents(model):
    '''print out top sentences'''
    print "sentences: {}".format(model)
    for i in np.argsort(mm.N_sk[:,model])[-10:]:
        print dd.raw_sents[i]


def print_words(model):
    '''print out top sentences'''
    print "words: {}".format(model)
    for i in np.argsort(mm.N_wk[:,model])[-10:]:
        print dd.num2word[i] + "," ,


def print_NPs(model, n):
    '''print out top sentences'''
    print "NPs: {}".format(model)
    counter = 0
    topnps = np.argsort(mm.N_wk[:,model])
    topnps = topnps[::-1]
    for i in topnps:
        if counter > n:
            break
        else:
            if len(dd.num2word[i].split(" ")) > 1:
                print dd.num2word[i] + "," ,
                counter += 1

print_NPs(QLM_K, 15)
print_sents(QLM_K)
print_words(GLM_K)
print_words(QLM_K)
