import pdb
import pickle
import random
import math
import itertools
import json
import numpy as np
import matplotlib.pyplot as plt
import pdb
from pylru import lrudecorator
from rookie import processed_location
from collections import Counter
from collections import defaultdict
from experiment.models import Models, Parameters
from rookie.classes import IncomingFile
from snippets.utils import flip
from snippets import log


iterations = 10


def random_z():
    draw = np.random.multinomial(1, [1/3.] * 3, size=1)[0].tolist()
    if draw[0] == 1:
        return "D"
    if draw[1] == 1:
        return "G"
    if draw[2] == 1:
        return "Q"


def get_doc_tokens(doc):
    '''
    Get the document's tokens
    '''
    doc_tokens = []
    for sentence_no in doc['sentences']:
        for token in doc['sentences'][sentence_no]['tokens']:
            tok = doc['sentences'][sentence_no]['tokens'][token]['word']
            doc_tokens.append(tok)
    doc_vocab_counter = Counter(doc_tokens)
    log.debug("DVOCAB||" + doc['url'] + "||" + json.dumps(doc_vocab_counter))
    return [i for i in set(doc_tokens)]


def get_doc_lm(doc):
    doc_pseudoc = defaultdict(int)
    doc_lm_counts = defaultdict(int)
    doc_vocab = get_doc_tokens(doc)
    for word in doc_vocab:
        doc_pseudoc[word] = 1
        doc_lm_counts[word] = 0
    doc_lm = {"counts": doc_lm_counts, "pseudocounts": doc_pseudoc}
    return doc_lm


def get_document(cloud_document):
    '''
    Get document data structure
    '''
    sentences = cloud_document['fields']['sentences'][0].split("||")
    document = {}
    document['sentences'] = {}
    document['url'] = cloud_document['fields']['url']
    for s in range(0, len(sentences)):
        sentence = sentences[s]
        tokens = sentence.split("&&")
        tokens_dict = {}
        for t in range(0, len(tokens)):
            if len(tokens[t]) > 0:
                tokens_dict[t] = {'word': tokens[t].lower(), 'z': random_z()}
        if len(tokens) > 5:  # ignore short sentence fragments
            document['sentences'][s] = {'tokens': tokens_dict}
    document['lm'] = get_doc_lm(document)
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
    for document in documents:
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


def lookup_p_lms(tokens, alpha):
    net_counts = {}
    output = {}
    for source in sources:
        net_counts[source] = alpha
    for token in tokens.keys():
        net_counts[tokens[token]['z']] += 1
    sum_counts = float(sum(v for k, v in net_counts.items()))
    for source in sources:
        output[source] = float(net_counts[source]) / sum_counts
    return output


def flip_for_z(p_tokens, p_lms, token, params):
    query = params.q + " " + params.term
    if token in query.split(" "):
        return "Q"
    ranges = []
    for source in sources:  # sources defined at top of file. bad
        ranges.append(p_tokens[source] * p_lms[source])
    winner = flip(ranges)
    return sources[winner]


@lrudecorator(1000)
def get_corpus_lm():
    corpus_lm = pickle.load(open("snippets/lm.p", "rb"))
    return corpus_lm

sources = ['G', 'Q', 'D']  # potential values for d


def search_for_documents(params):
    results = Models.search(params, overview=False)
    # results = pickle.load(open("pickled/oppveraresults.p", "r"))
    documents = [get_document(r) for r in results]
    return documents

p = Parameters()
p.q = "orleans parish prison"
p.term = "vera institute"
p.termtype = "organizations"

alpha = 1


z_flips_counts = []


class Sampler:

    def __init__(self, documents, iterations):
        self.documents = documents
        self.iterations = iterations
        self.query_lm = get_query_lm(documents)

    def lookup_p_token(self, token, lm_var, doc=None):
        if lm_var == "G":
            corpus_lm = get_corpus_lm()
            return corpus_lm[token]
        lm = None
        if lm_var == "D":
            lm = doc['lm']
        if lm_var == "Q":
            lm = self.query_lm
        numerator = lm['counts'][token] + lm['pseudocounts'][token]
        denom = sum(v for k, v in lm['counts'].items())
        # TODO: add decrements
        denom = denom + sum(v for k, v in lm['pseudocounts'].items())
        return float(numerator)/float(denom)

    def lookup_p_tokens(self, token, document):
        p_tokens = {}
        p_tokens['G'] = self.lookup_p_token(token['word'], 'G')
        p_tokens['Q'] = self.lookup_p_token(token['word'], 'Q')
        p_tokens['D'] = self.lookup_p_token(token['word'], 'D', document)
        return p_tokens

    def run(self):
        for iteration in range(0, self.iterations):
            print iteration
            z_flips_this_iteration = 0
            for document in self.documents:
                sent_keys = document['sentences']
                for sentence in sent_keys:
                    for token_no in document['sentences'][sentence]['tokens']:
                        token = document['sentences'][sentence]['tokens'][token_no]
                        p_tokens = self.lookup_p_tokens(token, document)
                        p_lms = lookup_p_lms(document['sentences'][sentence]['tokens'], alpha)
                        old_z = token['z']
                        new_z = flip_for_z(p_tokens, p_lms, token['word'], p)
                        if old_z != new_z:
                            z_flips_this_iteration += 1
                        document['sentences'][sentence]['tokens'][token_no]['z'] = new_z
                        if new_z != old_z:  # general LM is fixed
                            if new_z == "D":
                                document['lm']['counts'][token['word']] += 1
                            if new_z == "Q":
                                self.query_lm['counts'][token['word']] += 1
                            if old_z == "D" and document['lm']['counts'][token['word']] > 0:
                                document['lm']['counts'][token['word']] -= 1
                            if old_z == "Q" and self.query_lm['counts'][token['word']] > 0:
                                self.query_lm['counts'][token['word']] -= 1
                    log.debug("sentence_snapshot {} || {} || {} || {}".format(document['url'], iteration, sentence, json.dumps(document['sentences'][sentence])))
            log.debug("zflips || {} || {}".format(iteration, z_flips_this_iteration))

sampler = Sampler(search_for_documents(p), 10)
sampler.run()
