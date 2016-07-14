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
from utils import sent_to_string
import argparse
import cPickle as pickle
import ctypes
import sys
import string
import ujson as json
import numpy as np
import ipdb


parser = argparse.ArgumentParser()
parser.add_argument("-corpus", type=str, help="corpus")
ARGS = parser.parse_args()


from stop_words import get_stop_words
# os.system("./make.sh")

# To ignore numpy errors in pylint:
# pylint: disable=E1101

GLM_K = 0
QLM_K = 1

BETA = 5  # boost query words in priors for QLM

query = ["jail", "consent", "decree", "gusman"]

## set up model.  
class Model:
    pass

## token level data
class Dataset:
    pass




def run_sweep(dd, mm,starttok, endtok):

    mm.A_sk.dtype == "float32"
    mm.E_k.dtype == "float32"
    mm.E_k.dtype == "float32"
    mm.Q_ik.dtype == "float32"
    mm.N_wk.dtype == "float32"
    mm.N_k.dtype == "float32"
    mm.N_sk.dtype == "float32"


    libc.sweep(
            c_int(starttok), 
            c_int(endtok),
            as_ctypes(dd.tokens),
            as_ctypes(dd.docids),
            as_ctypes(dd.i_dk),
            c_int(K),
            c_int(V),
            as_ctypes(mm.A_sk),
            as_ctypes(mm.E_wk),
            as_ctypes(mm.E_k),
            as_ctypes(mm.Q_ik),
            as_ctypes(mm.N_wk),
            as_ctypes(mm.N_k),
            as_ctypes(mm.N_sk),
    )


def run_sweep_p(dd, mm, starttok, endtok):
    '''update tok range'''
    # python for now. should be written in a way that makes it be easy to xfer to C

    if endtok != Ntok:
        print "warning. not running on all tokens"
    for i in range(starttok, endtok):

        assert np.count_nonzero(np.isnan(mm.N_k)) == 0
        assert np.count_nonzero(np.isnan(mm.N_wk)) == 0
        assert np.count_nonzero(np.isnan(mm.N_sk)) == 0

        np.subtract(mm.N_k, mm.Q_ik[i], out=mm.N_k)
        np.subtract(mm.N_wk[dd.i_w[i]], mm.Q_ik[i], out=mm.N_wk[dd.i_w[i]])
        np.subtract(mm.N_sk[dd.i_s[i]], mm.Q_ik[i], out=mm.N_sk[dd.i_s[i]])

        #assert (mm.Q_ik < 0).sum() == 0
        #assert (mm.N_k < 0).sum() == 0
        #assert (mm.N_wk < 0).sum() == 0
        #assert (mm.N_sk < 0).sum() == 0

        
        #import ipdb
        #ipdb.set_trace()
        # assert mm.A_sk[i] == ALPHA
        ks = (mm.N_wk[dd.i_w[i]] + mm.E_wk[dd.i_w[i]])/(mm.N_k + mm.E_k) * (mm.A_sk[i] + mm.N_sk[dd.i_s[i]])

        # occassionnally have nonsense where ks is 0s b/c removed all mass in tn topic
        ks[dd.i_dk[i]] = max(1e-100, ks[dd.i_dk[i]]) # this avoids the NaNs. 
        ks[dd.i_dk[i]] = max(1e-100, ks[QLM_K])      # NOTE: ONLY 3 ks set. A dif w/ cvb0 in c
        ks[dd.i_dk[i]] = max(1e-100, ks[GLM_K])
        ks = ks / np.sum(ks)



        mm.Q_ik[i] = ks
        np.add(mm.N_k, ks, out=mm.N_k)
        np.add(mm.N_wk[dd.i_w[i]], ks, out=mm.N_wk[dd.i_w[i]])
        np.add(mm.N_sk[dd.i_s[i]], ks, out=mm.N_sk[dd.i_s[i]])



SW = get_stop_words('en') + ["city", "new", "orleans", "lens", "report", "said", "-lrb-", "-rrb-", "week"]
SW = SW + [o for o in string.punctuation] + [str(o) for o in range(0, 1000)]
SW = SW + ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
SW = SW + ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
SW = SW + ["a.m.", "p.m."]

libc = ctypes.CDLL("./cvb0.so")



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
    dd.i_dk = [] # maps i -> dk
    s_i = defaultdict(list)
    i = 0
    raw_sents = {}
    alpha_is = []
    for docid,line in enumerate(open("lens.anno")):
        if docid > 20: break 
        doc = json.loads(line)["text"]
        hit = 0
        for s_ix, sent in enumerate(doc['sentences']):
            reals = [word for word in sent["tokens"] if word.lower() not in SW]
            s_i[sentences] = []
            if len(reals) > 1: # need more than 1 word for sentence. fixes nan weirdness
                for word in reals:
                    
                    i_s.append(sentences) # building a vector of sentences for each token, i
                    dd.i_dk.append(docid + 2)
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
                    dd.docids.append(sentences)
                raw_sents[sentences] = sent_to_string(sent)
                sentences += 1
        if hit == 1:
            print "Found hit"
        # have to loop 2x here b/c need to see if doc is a hit first
        for s_ix, sent in enumerate(doc['sentences']): 
            reals = [word for word in sent["tokens"] if word.lower() not in SW]
            for w in reals:
                hits.append(hit)

        D_ += 1

    # an I length vector mapping i->hit. hit = i's document matches query
    dd.hits = np.array(hits, dtype=np.uint32)
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
    dd.doc_counts = default_to_regular(doc_counts)
    dd.word2num = word2num
    dd.num2word = num2word
    dd.raw_sents = raw_sents # this won't scale to corpora that dont fit in memory. TODO, maybe
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
ALPHA = 10.0/(3 * K) # 3 here b/c there are 3 valid options for each Q(i)
ETA = 100.0/V
D = dd.D
S = dd.S
Ntok = len(dd.tokens)


def make_model(dd):
    '''set up the model'''
    print "Setting up model"
    mm = Model()
    mm.N_w = np.zeros(V, dtype=np.float32)

    ## counting pass could be expensive
    for ww in dd.tokens:
        mm.N_w[ww] += 1 

    ## priors
    mm.E_wk = ETA * np.ones((V,K), dtype=np.float32)
    for w in query:
        mm.E_wk[dd.word2num[w]][QLM_K] = BETA
    mm.E_k  = mm.E_wk.sum(0)
    mm.A_sk = np.zeros((Ntok,K), dtype=np.float32)
    for i in range(Ntok):
        dk = dd.i_dk[i]
        mm.A_sk[i][0] = ALPHA  # no Alpha for invalid Ks
        mm.A_sk[i][1] = ALPHA
        mm.A_sk[i][dk] = ALPHA
    mm.A_sk = np.asarray(mm.A_sk, dtype=np.float32)
    mm.Q_ik = np.zeros((Ntok,K), dtype=np.float32) # don't pickle this part
    # just for compatibility. not used in C code.
    mm.qfix = np.zeros(Ntok, dtype=np.int8)
    return mm


def fill_qi_randomly_and_count(dd, mm):
    '''i think its faster to let the algo converge than load empirical lm'''
    mm.N_k = np.zeros(K, dtype=np.float32)
    mm.N_sk = np.zeros((S, K), dtype=np.float32)
    mm.N_wk = np.zeros((V, K), dtype=np.float32)
    print "filling dataset randomly"
    mm.Q_ik = np.array(np.random.dirichlet(np.ones(K), Ntok), dtype=np.float32)
    assert mm.Q_ik.shape[0] == Ntok
    for i_ in range(Ntok):
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

        # if np.sum(infodot(Q, np.log(topics[w,:]))) == 0:
        #    import ipdb
        #    ipdb.set_trace()
        ll += infodot(Q, np.log(topics[w,:]))
        # E[log P(z)]: skip i'm confused. have to eval per doc dirichlets i think
        # E[log Q(z)]

        lg_q = np.log(Q)

        lg_q[np.isnan(lg_q)] = 0  # NaNs will cause whole infodot to be a Nan so no LL reading
        
        if np.isnan(infodot(Q, lg_q)):
            import ipdb
            ipdb.set_trace()
        ll += infodot(Q, lg_q)
    return np.nan_to_num(ll)

mm = make_model(dd)

fill_qi_randomly_and_count(dd, mm)

print "[*] Prelims complete"
for itr in range(100):
    #run_sweep_p(dd,mm,0,Ntok)

    #import ipdb
    #ipdb.set_trace()
    run_sweep(dd,mm,0,Ntok)

    if itr % 10 == 0:
        print loglik(dd,mm)
        print "=== Iter",itr


def print_sents():
    '''print out top sentences QLM'''
    for i in np.argsort(mm.N_sk[QLM_K])[-10:]:
        print dd.raw_sents[i]


def print_words():
    '''print out top sentences QLM'''
    for i in np.argsort(mm.N_wk[QLM_K])[-10:]:
        print dd.num2word[i] + "," , 

print_sents()
print_words()
