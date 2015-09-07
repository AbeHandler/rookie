import pdb
import pickle
import numpy as np
from rookie.classes import IncomingFile

corpus_lm = pickle.load(open("snippets/lm.p", "rb"))

vocab = corpus_lm.keys()

file_loc = "/Users/abramhandler/research/rookie/data/lens_processed/"
fn = "54b47042283234b7d34df98a19c2252acc7947becc8a257935fc0f9c"

inf = IncomingFile(file_loc + fn)

query = ["common", "core", "gary", "robichaux"]

document = {}

for count in range(0, len(inf.doc.sentences)):
    document[count] = [i.raw for i in inf.doc.sentences[count].tokens]

pdb.set_trace()

z_s = []

'''
Setup pseudocounts
'''
query_lm_pseudocounts = {}
for word in vocab:
    query_lm_pseudocounts[word] = 1


doc_lm_pseudocounts = {}
for word in vocab:
    doc_lm_pseudocounts[word] = 1

sentence_pseudo_counts = {}
sentence_pseudo_counts['D'] = 1
sentence_pseudo_counts['Q'] = 1
sentence_pseudo_counts['G'] = 1
