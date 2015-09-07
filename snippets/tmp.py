import pickle
import numpy as np
from rookie.classes import IncomingFile

corpus_lm = pickle.load(open("snippets/lm.p", "rb"))

vocab = corpus_lm.keys()

file_loc = "/Users/abramhandler/research/rookie/data/lens_processed/"
fn = "54b47042283234b7d34df98a19c2252acc7947becc8a257935fc0f9c"

inf = IncomingFile(file_loc + fn)
sentences = inf.doc.sentences

'''
Setup pseudocounts
'''
query_lm_pseudocounts = {}
for word in vocab:
    query_lm_pseudocounts[word] = 1


doc_lm_pseudocounts = {}
for word in vocab:
    doc_lm_pseudocounts[word] = 1

pi_pseudocounts = {}
pi_pseudo_counts['D'] = 1
pi_pseudo_counts['Q'] = 1
pi_pseudo_counts['G'] = 1


def draw_from_dirichlet():
    return np.random.dirichlet(1, .5, 1)[0]

print "s"
