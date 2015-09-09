import pdb
import pickle
import random
import math
import itertools
import json
import numpy as np
import matplotlib.pyplot as plt
import pickle

import pdb

from rookie import processed_location
from collections import Counter
from collections import defaultdict
from rookie.classes import IncomingFile
from snippets.utils import flip
from snippets import log

import logging

LOG_FILENAME = 'run_log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

iterations = 100

pi_pseudo_counts = {'D': 1, 'Q': 1, 'G': 1}

lms = {}  # variable to hold the langauge model counts/pseudocounts

'''
Load the precomputed corpus language model
'''
corpus_lm = pickle.load(open("snippets/lm.p", "rb"))

'''
Load the sample file and query
'''

query = [["orleans", "parish", "prison"], ["vera", "institute"]]

# query = [["common", "core"], ["gary", "robichaux"]]

sources = ['G', 'Q', 'D']  # potential values for d

fns = ["e2c1d798aca417cf982268410274b07010c78fa1f638343455c87069",
       "48a455f3b50685d18e7be9e5bb3bacbbafb582a898659812d9cb1aa1"]

documents = {}

part of reason query + doc are tied is qurey vocab should be across all docs

def get_doc_tokens(inf):
    '''
    Get the document's tokens
    '''
    doc_tokens = [i.raw.lower() for i in inf.doc.tokens]
    doc_vocab_counter = Counter(doc_tokens)
    log.debug(inf.filename + ", " + json.dumps(doc_vocab_counter))
    return set(doc_tokens)


def get_document(inf):
    '''
    Get document data structure
    '''
    document = {}
    for s in range(0, len(inf.doc.sentences)):
        tokens_dict = {}
        tokens = [i.raw.lower() for i in inf.doc.sentences[s].tokens]
        for t in range(0, len(tokens)):
            tokens_dict[t] = {'word': tokens[t], 'z': random_z()}
        document[s] = {'tokens': tokens_dict}
    return document

'''
Load up documents
'''
for fn in range(0, fns):
    inf = IncomingFile(processed_location + "/" + fn)
    doc_vocab = get_doc_tokens(inf)
    documents[fn] = get_document(inf)


'''
Setup pseudocounts and counts for doc/query LMs + sentence distributions.
'''
query_pseudoc = defaultdict(int)
query_lm_counts = defaultdict(int)
for word in doc_vocab:
    query_pseudoc[word] = 1
    query_lm_counts[word] = 0

doc_pseudoc = defaultdict(int)
doc_lm_counts = defaultdict(int)
for word in doc_vocab:
    doc_pseudoc[word] = 1
    doc_lm_counts[word] = 0

lms["Q"] = {"counts": query_lm_counts, "pseudocounts": query_pseudoc}
lms["D"] = {"counts": doc_lm_counts, "pseudocounts": doc_pseudoc}


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
    return float(numerator)/float(denom)


def lookup_p_lms(tokens):
    net_counts = {}
    output = {}
    for source in sources:
        net_counts[source] = pi_pseudo_counts[source]
    for token in tokens.keys():
        net_counts[tokens[0]['z']] += 1
    sum_counts = float(sum(v for k, v in net_counts.items()))
    for source in sources:
        output[source] = float(net_counts[source]) / sum_counts
    return output


def flip_for_z(p_tokens, p_lms, token):
    for term in query:
        if token in term:
            return "Q"
    ranges = []
    for source in sources:  # sources defined at top of file. bad
        ranges.append(p_tokens[source] * p_lms[source])
    winner = flip(ranges)
    return sources[winner]

z_flips_counts = []
grand_total_score_keeping = {}
grand_total_score_keeping["Q"] = []
grand_total_score_keeping["D"] = []

for i in range(0, iterations):
    print i
    for doc in documents:
        document = documents[doc]
        z_flips_this_iteration = 0
        for sentence in document.keys():
            # pi_counts = document[sentence]['pi_counts']
            for token_no in document[sentence]['tokens']:
                token = document[sentence]['tokens'][token_no]
                p_tokens = {}
                p_tokens['G'] = corpus_lm[token['word']]
                p_tokens['Q'] = lookup_p_token(token['word'], 'Q')
                p_tokens['D'] = lookup_p_token(token['word'], 'D')
                p_lms = lookup_p_lms(document[sentence]['tokens'])
                old_z = token['z']
                new_z = flip_for_z(p_tokens, p_lms, token['word'])
                if old_z != new_z:
                    z_flips_this_iteration += 1
                document[sentence]['tokens'][token_no]['z'] = new_z
                if new_z != old_z:  # general LM is fixed
                    if new_z != "G":
                        lms[new_z]['counts'][token['word']] += 1
                    if old_z != "G":
                        if lms[old_z]['counts'][token['word']] > 0:
                            lms[old_z]['counts'][token['word']] -= 1
        if z_flips_this_iteration == 0:
            z_flips_counts.append(0)
        else:
            z_flips_counts.append(math.log(z_flips_this_iteration))
