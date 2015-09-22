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


class DocFetcher:

    '''
    Searches for documents on Amazon cloudsearch and converts them into
    nested dictionaries with language models for the sampler
    '''

    def __init__(self):
        self.sources = ['G', 'Q', 'D']

    def get_doc_tokens(self, doc):
        '''
        Get the document's tokens
        '''
        doc_tokens = []
        for sentence_no in doc['sentences']:
            for token in doc['sentences'][sentence_no]['tokens']:
                tok = doc['sentences'][sentence_no]['tokens'][token]['word']
                doc_tokens.append(tok)
        doc_vocab_counter = Counter(doc_tokens)
        log.debug("DVOC||" + doc['url'] + "||" + json.dumps(doc_vocab_counter))
        return [i for i in set(doc_tokens)]

    def get_doc_lm(self, doc):
        doc_pseudoc = defaultdict(int)
        doc_lm_counts = defaultdict(int)
        doc_vocab = self.get_doc_tokens(doc)
        for word in doc_vocab:
            doc_pseudoc[word] = 1
            doc_lm_counts[word] = 0
        pseudocounts_tot = sum(doc_pseudoc.values())
        counts_tot = sum(doc_lm_counts.values())
        doc_lm = {"counts_tot": counts_tot, "counts": doc_lm_counts, "pseudocounts": doc_pseudoc, "pseudo_tot": pseudocounts_tot}
        return doc_lm

    def get_document(self, cloud_document):
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
                    draw = np.random.multinomial(1, [1/3.] * 3, size=1)[0].tolist()
                    tokens_dict[t] = {'word': tokens[t].lower(), 'z': self.sources[draw.index(1)]}
            if len(tokens) > 5:  # ignore short sentence fragments
                zcounts = {"D": 0, "Q": 0, "G": 0}
                for token in tokens_dict:
                    zcounts[tokens_dict[token]['z']] += 1
                document['sentences'][s] = {'tokens': tokens_dict, 'zcounts': zcounts, 'zpseudo': {"D": 1, "Q": 1, "G": 1}}
        document['lm'] = self.get_doc_lm(document)
        return document

    def search_for_documents(self, params):
        results = Models.search(params, overview=False)
        # results = pickle.load(open("pickled/oppveraresults.p", "r"))
        documents = [self.get_document(r) for r in results]
        return documents


class Sampler:

    def __init__(self, documents, iterations, params):
        self.documents = documents
        self.iterations = iterations
        self.query_lm = self.get_query_lm(documents)
        self.corpus_lm = pickle.load(open("snippets/lm.p", "rb"))
        self.sources = ['G', 'Q', 'D']
        self.params = params

    def get_query_vocab(self, documents):
        query_vocab = []
        for document in documents:
            doc_vocab = document['lm']['counts'].keys()
            query_vocab = query_vocab + doc_vocab
        return [i for i in set(query_vocab)]

    def get_query_lm(self, documents):
        query_pseudoc = defaultdict(int)
        query_lm_counts = defaultdict(int)
        all_words_from_docs = self.get_query_vocab(documents)
        for word in all_words_from_docs:
            query_pseudoc[word] = 1
            query_lm_counts[word] = 0
        counts_tot = sum(query_lm_counts.values())
        return {"counts_tot": counts_tot, "counts": query_lm_counts, "pseudocounts": query_pseudoc, "pseudo_tot": sum(query_pseudoc.values())}

    def lookup_p_lms(self, tokens, alpha, token_no, zcounts, zpseudo):
        missing_z = tokens[token_no]['z']
        denom = sum(zcounts.values()) - 1 + sum(zpseudo.values())
        output = {}
        for source in self.sources:
            if source == missing_z:
                num = zcounts[source] - 1 + zpseudo[tokens[token_no]['z']]
            else:
                num = zcounts[source] + zpseudo[tokens[token_no]['z']]
            output[source] = float(num) / denom
        return output

    def flip_for_z(self, p_tokens, p_lms, token):
        query = self.params.q + " " + self.params.term
        if token in query.split(" "):
            return "Q"
        ranges = []
        for source in self.sources:  # sources defined at top of file. bad
            ranges.append(p_tokens[source] * p_lms[source])
        winner = flip(ranges)
        return self.sources[winner]

    def lookup_p_token(self, token, lm_var, doclm=None):
        if lm_var == "G":
            return self.corpus_lm[token['word']]
        if lm_var == "D":
            lm = doclm
        if lm_var == "Q":
            lm = self.query_lm
        numerator = lm['counts'][token['word']] + lm['pseudocounts'][token['word']]
        denom = lm['counts_tot']
        denom = denom + lm['pseudo_tot']
        # pretend you have not seen this token yet...
        denom = denom - 1  # for so query_lm and doclm have -1 tokens
        if token['z'] == lm_var:  # if the token's z value adds to the numerator count
            numerator -= 1  # decrement the numerator
        return float(numerator)/float(denom)

    def lookup_p_tokens(self, token, document):
        p_tokens = {}
        p_tokens['G'] = self.lookup_p_token(token, 'G')
        p_tokens['Q'] = self.lookup_p_token(token, 'Q')
        p_tokens['D'] = self.lookup_p_token(token, 'D', document['lm'])
        return p_tokens

    def sample_token(self, token, token_no, sentence, document, alpha, zcounts, zpseudo):
        p_tokens = self.lookup_p_tokens(token, document)
        p_lms = self.lookup_p_lms(document['sentences'][sentence]['tokens'], alpha, token_no, zcounts, zpseudo)
        new_z = self.flip_for_z(p_tokens, p_lms, token['word'])
        return new_z

    def adjust_sentence_z_counts(self, zcounts, oldz, newz):
        zcounts[oldz] -= 1
        zcounts[newz] += 1
        return zcounts

    def run(self, alpha):
        z_flips_counts = []
        for iteration in range(0, self.iterations):
            print iteration
            z_flips_this_iteration = 0
            for document in self.documents:
                sent_keys = document['sentences']
                for sentence in sent_keys:
                    for token_no in document['sentences'][sentence]['tokens']:
                        token = document['sentences'][sentence]['tokens'][token_no]
                        new_z = self.sample_token(token, token_no, sentence, document, alpha, document['sentences'][sentence]['zcounts'], document['sentences'][sentence]['zpseudo'])
                        if token['z'] != new_z:
                            z_flips_this_iteration += 1
                        if new_z != token['z']:  # general LM is fixed
                            document['sentences'][sentence]['zcounts'] = self.adjust_sentence_z_counts(document['sentences'][sentence]['zcounts'], token['z'], new_z)
                            if new_z == "D":
                                document['lm']['counts'][token['word']] += 1
                            if new_z == "Q":
                                self.query_lm['counts'][token['word']] += 1
                            if token['z'] == "D" and document['lm']['counts'][token['word']] > 0:
                                document['lm']['counts'][token['word']] -= 1
                            if token['z'] == "Q" and self.query_lm['counts'][token['word']] > 0:
                                self.query_lm['counts'][token['word']] -= 1
                        document['sentences'][sentence]['tokens'][token_no]['z'] = new_z
                    log.debug("sentence_snapshot {} || {} || {} || {}".format(document['url'], iteration, sentence, json.dumps(document['sentences'][sentence])))
            log.debug("zflips || {} || {}".format(iteration, z_flips_this_iteration))

p = Parameters()
p.q = "coastal restoration"
p.term = "bobby jindal"
p.termtype = "people"

df = DocFetcher()
docs = df.search_for_documents(p)
pickle.dump(docs, open("docs.p", "w"))
docs = pickle.load(open("docs.p", "r"))
sampler = Sampler(docs, 10, p)
sampler.run(1)
