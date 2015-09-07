import pdb
import pickle
import numpy as np
from rookie.classes import IncomingFile

'''
Load the precomputed corpus language model
'''

corpus_lm = pickle.load(open("snippets/lm.p", "rb"))

vocab = corpus_lm.keys()

'''
Load the sample file and query
'''

file_loc = "/Users/abramhandler/research/rookie/data/lens_processed/"
fn = "54b47042283234b7d34df98a19c2252acc7947becc8a257935fc0f9c"
inf = IncomingFile(file_loc + fn)

query = ["common", "core", "gary", "robichaux"]

'''
Setup pseudocounts and counts
'''
query_pseudoc = {}
query_lm_counts = {}
for word in vocab:
    query_pseudoc[word] = 1
    query_lm_counts[word] = 0

doc_pseudoc = {}
doc_lm_counts = {}
for word in vocab:
    doc_pseudoc[word] = 1
    doc_lm_counts[word] = 0

sentence_pseudo_counts = {'D': 1, 'Q': 1, 'G': 1}

lms = {}
lms["query"] = {"counts": query_lm_counts, "pseudocounts": query_pseudoc}
lms["document"] = {"counts": doc_lm_counts, "pseudocounts": doc_pseudoc}


def random_z():
    draw = np.random.multinomial(1, [1/3.] * 3, size=1)[0].tolist()
    if draw[0] == 1:
        return "D"
    if draw[1] == 1:
        return "G"
    if draw[2] == 1:
        return "Q"


def lookup_p_token(token, lm):
    numerator = lms[lm]['counts'][token] + lms[lm]['pseudocounts'][token]
    denom = sum(v for k, v in lms[lm]['counts'].items())
    denom = denom + sum(v for k, v in lms[lm]['pseudocounts'].items())
    pdb.set_trace()
    return float(numerator)/float(denom)


'''
Setup data structure and initialize sampler
'''
document = {}
for s in range(0, len(inf.doc.sentences)):
    tokens_dict = {}
    tokens = [i.raw.lower() for i in inf.doc.sentences[s].tokens]
    for t in range(0, len(tokens)):
        tokens_dict[t] = {'word': tokens[t], 'z': random_z()}
    sentence_pi_counts = {'D': 0, 'Q': 0, 'G': 0}
    document[s] = {'pi_counts': sentence_pi_counts, 'tokens': tokens_dict}

iterations = 1000

for i in range(0, iterations):
    for sentence in document.keys():
        pi_counts = document[sentence]['pi_counts']
        for token_no in document[sentence]['tokens']:
            token = document[sentence]['tokens'][token_no]
            p_corpus_lm = corpus_lm[token]['word']
            p_query_lm = lookup_p_token(token, 'query')
