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
import ctypes
import string
import ujson as json
import numpy as np



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
        import ipdb
        ipdb.set_trace()
        np.subtract(mm.N_k, mm.Q_ik[i], out=mm.N_k)
        np.subtract(mm.N_wk[dd.i_w[i]], mm.Q_ik[i], out=mm.N_wk[dd.i_w[i]])
        np.subtract(mm.N_sk[dd.i_s[i]], mm.Q_ik[i], out=mm.N_sk[dd.i_s[i]])
        
        assert np.where(mm.N_k < 0)[0].shape == 0
        assert np.where(mm.N_wk < 0)[0].shape == 0
        assert np.where(mm.N_sk < 0)[0].shape == 0

        o = mm.N_wk + eta
        oo = mm.N_k + (dd.V * eta)

        # mm.N_k => N_k vec of K
        # mm.N_wk => need to construct a 3-place vec of Q, D and G language models. rest of K are 0
        # mm.N_sk => again, the sentence probabilities
        # decrement: N_wk, N_K, N_kj
        # k_probs = len(K) vec
        # increment: N_wk, N_K, N_kj


SW = get_stop_words('en') + ["city", "new", "orleans", "lens", "report", "said", "-lrb-", "-rrb-"]
SW = SW + [o for o in string.punctuation]

libc = ctypes.CDLL("./cvb0.so")


def fill_emprical_language_models(dd, mm):
    '''find p(W|K) for each doc, G and Q lm'''
    smoothing = 1
    mm.emprical_N_wk = np.zeros((K,V), dtype=np.float32)
    for k in range(K):
        tot_words = sum(dd.doc_counts[k]) + (smoothing * V)
        for v in range(V):
            try:
                tot_word = tot_word = dd.doc_counts[k][v] + smoothing
            except KeyError:  # i.e. word does not appear
                tot_word = smoothing
            mm.emprical_N_wk[k][v] = tot_word/tot_words


def build_dataset():
    ## load data.  will be faster to pre-numberize it.

    # docids are offset by 2. First 2 "docids" are reserved for global and query lm

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
    for docid,line in enumerate(open("lens.anno")):
        if docid > 25: break # TODO: un-shorten dataset
        doc = json.loads(line)["text"]
        hit = 0
        for s_ix, sent in enumerate(doc['sentences']):
            reals = [word for word in sent["tokens"] if word.lower() not in SW]
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
                dd.tokens.append(n)
                i_w.append(n)
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
    assert dd.i_w.shape[0] == dd.i_s.shape[0]
    # a S length vector w/ the doc id for each S
    dd.docids = np.array(dd.docids, dtype=np.uint32) 
    dd.tokens = np.array(dd.tokens, dtype=np.uint32)
    dd.D = D_ # cant look at end of array b/c is 2 extra
    dd.V = len(word2num)
    dd.Ntok = len(dd.tokens)
    dd.doc_counts = doc_counts
        
    return dd, word2num, num2word

dd, WORD2NUM, NUM2WORD = build_dataset()

K = dd.D + 1 + 1 # i.e. D language models, plus a Q model, plus a G model
# for any given Q_i, only 3 of these will be relevant
V = len(WORD2NUM)
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

def empirical_init(dd, mm):
    '''init w/ emprical language models from D and G'''
    # if a doc is not responsive to a query, there are only 2 options for the token: D or G
    # if it is responsive to query, there are 3 options  

    for i_ in range(Ntok):
        w = dd.i_w[i_]
        mm.Q_ik[i_][GLM_K] = mm.emprical_N_wk[GLM_K][w]
        if dd.hits[i_] == 1:
            mm.Q_ik[i_][QLM_K] = mm.emprical_N_wk[GLM_K][w] * 2 # init query lm to global X 2 ? 
        dk = dd.i_dk[i_] # i's document lm

        mm.Q_ik[i_][dk] = mm.emprical_N_wk[dk][w]
        mm.Q_ik[i_] = mm.Q_ik[i_]/np.sum(mm.Q_ik[i_]) # normalize
        assert round(np.sum(mm.Q_ik[i_]), 5) == 1.
        assert np.where(mm.Q_ik[i_] != 0)[0].shape[0] <= 3 # no more than 3 ks turned on per row

    for i_ in range(Ntok):
        ss = dd.i_s[i_]
        idk = dd.i_dk[i_] # tokens document language model
        # print i_, ss
        w = dd.i_w[i_]
        for k in range(K):
            if k > 1 and k != idk:
                assert mm.Q_ik[i_][k] == 0.0
        for k in range(K):
            mm.N_sk[ss][k] += mm.Q_ik[i_][k]
            try:
                assert np.where(mm.N_sk[ss] != 0)[0].shape[0] <= 3 # no more than 3 ks turned on per N_sk
            except:
                print i_, k, mm.N_sk[ss], mm.Q_ik[i_]
                import ipdb
                ipdb.set_trace()
            mm.N_k[k] += mm.Q_ik[i_][k]
            mm.N_wk[w][k] += mm.Q_ik[i_][k]



mm = make_model()

fill_emprical_language_models(dd, mm)
empirical_init(dd, mm)

for itr in range(100):
    # print loglik(dd, mm)
    run_sweep(dd,mm, 0,len(dd.tokens))
#    print "=== Iter",itr


for i in np.argsort(mm.emprical_N_wk[QLM_K])[-5:]:
    print NUM2WORD[i]
