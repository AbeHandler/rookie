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

iterations = 50

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

sources = ['G', 'Q', 'D']  # potential values for d

fns = [o.replace("\n", "") for o in open("snippets/oppverafiles.txt", "r")]

documents = {}


def sentence_to_human(sentence):
    human = [(k, v) for k,v in sentence.items()]
    human.sort(key=lambda x: x[0])
    human = " ".join([o[1]['word'] for o in human])
    return human


def random_z():
    draw = np.random.multinomial(1, [1/3.] * 3, size=1)[0].tolist()
    if draw[0] == 1:
        return "D"
    if draw[1] == 1:
        return "G"
    if draw[2] == 1:
        return "Q"


def get_doc_tokens(inf):
    '''
    Get the document's tokens
    '''
    doc_tokens = [i.raw.lower() for i in inf.doc.tokens]
    doc_vocab_counter = Counter(doc_tokens)
    log.debug("DVOCAB||" + inf.filename + "||" + json.dumps(doc_vocab_counter))
    return [i for i in set(doc_tokens)]


def get_doc_lm(inf):
    doc_pseudoc = defaultdict(int)
    doc_lm_counts = defaultdict(int)
    doc_vocab = get_doc_tokens(inf)
    for word in doc_vocab:
        doc_pseudoc[word] = 1
        doc_lm_counts[word] = 0
    doc_lm = {"counts": doc_lm_counts, "pseudocounts": doc_pseudoc}
    return doc_lm


def get_document(inf):
    '''
    Get document data structure
    '''
    document = {}
    for s in range(0, len(inf.doc.sentences)):
        tokens = [o.raw for o in inf.doc.sentences[s].tokens]
        tokens_dict = {}
        for t in range(0, len(tokens)):
            tokens_dict[t] = {'word': tokens[t].lower(), 'z': random_z()}
        document[s] = {'tokens': tokens_dict}
    document['lm'] = get_doc_lm(inf)
    document['fn'] = inf.filename
    return document


def get_documents(fns):
    '''
    Load up documents
    '''
    documents = {}
    for fn in range(0, len(fns)):
        inf = IncomingFile(processed_location + "/" + fns[fn])
        documents[fn] = get_document(inf)
    return documents


def get_query_vocab(documents):
    query_vocab = []
    for d in documents.keys():
        document = documents[d]
        doc_vocab = document['lm']['counts'].keys()
        query_vocab = query_vocab + doc_vocab
    return [i for i in set(query_vocab)]


def get_query_lm(documents):
    query_pseudoc = defaultdict(int)
    query_lm_counts = defaultdict(int)
    all_words_from_docs = get_query_vocab(documents)
    for word in all_words_from_docs:
        query_pseudoc[word] = 1
        query_lm_counts[word] = 0
    return {"counts": query_lm_counts, "pseudocounts": query_pseudoc}


documents = get_documents(fns)
query_lm = get_query_lm(documents)


'''
Setup pseudocounts and counts for doc/query LMs + sentence distributions.
'''


def lookup_p_token(token, lm_var, doc=None):
    if lm_var == "G":
        return corpus_lm[token]
    lm = None
    if lm_var == "D":
        lm = doc['lm']
    if lm_var == "Q":
        lm = query_lm
    numerator = lm['counts'][token] + lm['pseudocounts'][token]
    denom = sum(v for k, v in lm['counts'].items())
    denom = denom + sum(v for k, v in lm['pseudocounts'].items())  # TODO: add decrements
    return float(numerator)/float(denom)


def lookup_p_lms(tokens):
    net_counts = {}
    output = {}
    for source in sources:
        net_counts[source] = pi_pseudo_counts[source]
    for token in tokens.keys():
        net_counts[tokens[token]['z']] += 1
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

for i in range(0, iterations):
    print i
    for doc in documents:
        document = documents[doc]
        z_flips_this_iteration = 0
        sent_keys = (i for i in document.keys() if i != ("lm") and i != "fn")
        for sentence in sent_keys:
            for token_no in document[sentence]['tokens']:
                token = document[sentence]['tokens'][token_no]
                p_tokens = {}
                p_tokens['G'] = lookup_p_token(token['word'], 'G')
                p_tokens['Q'] = lookup_p_token(token['word'], 'Q')
                p_tokens['D'] = lookup_p_token(token['word'], 'D', document)
                p_lms = lookup_p_lms(document[sentence]['tokens'])
                old_z = token['z']
                new_z = flip_for_z(p_tokens, p_lms, token['word'])
                if old_z != new_z:
                    z_flips_this_iteration += 1
                document[sentence]['tokens'][token_no]['z'] = new_z
                if new_z != old_z:  # general LM is fixed
                    if new_z == "D":
                        document['lm']['counts'][token['word']] += 1
                    if new_z == "Q":
                        query_lm['counts'][token['word']] += 1
                    if old_z == "D" and document['lm']['counts'][token['word']] > 0:
                        document['lm']['counts'][token['word']] -= 1
                    if old_z == "Q" and query_lm['counts'][token['word']] > 0:
                        query_lm['counts'][token['word']] -= 1
            log.debug("sentence_snapshot {} || {} || {} || {}".format(document['fn'], i, sentence, json.dumps(document[sentence])))
        log.debug("zflips || {} || {} || {}".format(document['fn'], i, doc, z_flips_this_iteration))
