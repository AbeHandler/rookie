import pdb
import pickle
import random
import math
import itertools
import numpy as np
import matplotlib.pyplot as plt
import pickle

import pdb

from rookie import processed_location
from collections import Counter
from collections import defaultdict
from rookie.classes import IncomingFile
from snippets.utils import flip

jaccard_threshold = .75

pi_pseudo_counts = {'D': 1, 'Q': 1, 'G': 1}

lms = {}  # variable to hold the langauge model counts/pseudocounts

'''
Load the precomputed corpus language model
'''

corpus_lm = pickle.load(open("snippets/jk_lm.p", "rb"))

vocab = corpus_lm.keys()

'''
Load the sample file and query
'''

query = [["orleans", "parish", "prison"], ["vera", "institute"]]

# query = [["common", "core"], ["gary", "robichaux"]]

sources = ['G', 'Q', 'D']  # potential values for d

fns = ["e2c1d798aca417cf982268410274b07010c78fa1f638343455c87069"]  # "48a455f3b50685d18e7be9e5bb3bacbbafb582a898659812d9cb1aa1"]

fn = fns[0]

inf = IncomingFile(processed_location + "/" + fn)

documents = {}


def get_doc_tokens(inf):
    '''
    Get the document's tokens
    '''
    all_tokens = [str(i).lower() for i in inf.doc.people] + [str(i) for i in inf.doc.organizations]

    ngrams = inf.doc.ngrams
    for n in ngrams:
        all_tokens.append(" ".join([i.raw for i in n]).lower())

    return all_tokens

all_tokens = get_doc_tokens(inf)
doc_vocab = [i.lower() for i in all_tokens]
doc_vocab_counter = Counter(doc_vocab)  # count of each word in doc
doc_vocab = [i for i in set(doc_vocab)]


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
    sum_counts = float(sum(v for k,v in net_counts.items()))
    for source in sources:
        output[source] = float(net_counts[source]) / sum_counts
    return output


def flip_for_z(p_tokens, p_lms, token):
    for term in query:
        intersect = float(len([i for i in set(term).intersection(set(token.split(" ")))]))
        union = float(len([i for i in set(term).union(set(token.split(" ")))]))
        if (intersect/union) > jaccard_threshold:
            return "Q"
    ranges = []
    for source in sources: # sources defined at top of file. bad
        ranges.append(p_tokens[source] * p_lms[source])
    winner = flip(ranges)
    return sources[winner]


def flip_for_pi_count(pi_pseudo_c, sentence):
    denom = sum(v for k, v in pi_pseudo_c.items())
    # denom = float(denom + sum(v for k, v in sentence['pi_counts'].items()))
    total = 0.
    ranges = {}
    tokens = sentence['tokens']
    if len(tokens) == 0:
        return "NA"
    ranges = []
    for source in sources:
        old_total = total
        # p_counts = (pi_pseudo_c[source] + sentence['pi_counts'][source])/denom
        z_count_source = len([i for i in tokens if tokens[i]['z'] == source])
        p_zs = float(z_count_source) / float(len(tokens))
        source_area = p_zs * p_counts
        ranges.append(source_area)
    winner = flip(ranges)
    return sources[winner]


def get_document(inf):
    '''
    Setup data structure and initialize sampler
    '''
    document = {}
    for s in range(0, len(inf.doc.sentences)):
        tokens_dict = {}
        pplorgsngrams = [str(i).lower() for i in inf.doc.sentences[s].ner if i.type == "ORGANIZATION" or i.type == "PEOPLE"]
        ngrams = [i for i in inf.doc.sentences[s].ngrams]
        for n in ngrams:
            pplorgsngrams.append(" ".join([i.raw for i in n]).lower())
        tokens = pplorgsngrams
        for t in range(0, len(tokens)):
            tokens_dict[t] = {'word': tokens[t], 'z': random_z()}
        # sentence_pi_counts = {'D': 0, 'Q': 0, 'G': 0}
        document[s] = {'tokens': tokens_dict}
    return document

documents[0] = get_document(inf)

document = documents[0]

iterations = 10

z_flips_counts = []
grand_total_score_keeping = {}
grand_total_score_keeping["Q"] = []
grand_total_score_keeping["D"] = []

for i in range(0, iterations):
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
                        lms[new_z]['counts'][token['word']] += 1 # increment the LM
                    if old_z != "G" and lms[old_z]['counts'][token['word']] > 0:
                        lms[old_z]['counts'][token['word']] -= 1

        # some score keeping for the model to be cleaned up later. TODO
        score_keeping = []
        all_tokens = []
        for sentence in document.keys():
            sentence_tokens = document[sentence]['tokens']
            for word_no in sentence_tokens.keys():
                word = document[sentence]['tokens'][word_no]
                all_tokens.append((word['word'], word['z']))
        for w in doc_vocab_counter:
            isquery = sum(1 for t in all_tokens if t[0] == w and t[1] == "Q")
            score_keeping.append((w, doc_vocab_counter[w], isquery))
        grand_total_score_keeping["Q"].append(score_keeping)

        score_keeping = []
        for w in doc_vocab_counter:
            isquery = sum(1 for t in all_tokens if t[0] == w and t[1] == "D")
            score_keeping.append((w, doc_vocab_counter[w], isquery))
        grand_total_score_keeping["D"].append(score_keeping)

        if z_flips_this_iteration == 0:
            z_flips_counts.append(0)
        else:
            z_flips_counts.append(math.log(z_flips_this_iteration))


'''
Score keeping and debugging
'''

most_common_labeled_q = []
joined = [i for i in itertools.chain(*grand_total_score_keeping["Q"])]
for word in doc_vocab_counter:
    tmp = [o for o in joined if o[0] == word]
    total_occurances = float(sum(i[1] for i in tmp))
    total_occurances_zs = float(sum(i[2] for i in tmp))
    if total_occurances_zs == 0:
        most_common_labeled_q.append((word, 0))
    else:
        most_common_labeled_q.append((word, total_occurances_zs/total_occurances))
most_common_labeled_q.sort(key=lambda x: x[1])


most_common_labeled_d = []
joined = [i for i in itertools.chain(*grand_total_score_keeping["D"])]
for word in doc_vocab_counter:
    tmp = [o for o in joined if o[0] == word]
    total_occurances = float(sum(i[1] for i in tmp))
    total_occurances_zs = float(sum(i[2] for i in tmp))
    if total_occurances_zs == 0:
        most_common_labeled_d.append((word, 0))
    else:
        most_common_labeled_d.append((word, total_occurances_zs/total_occurances))
most_common_labeled_d.sort(key=lambda x: x[1])


def get_pct_of_sentence(sentence_tokens, target):
    assert (target == "D" or target=="Q" or target=="G")
    total = 0
    target_total = 0
    for key in sentence_tokens.keys():
        total += 1
        zval = sentence_tokens[key]['z'] 
        if zval == target:
            target_total +=1
    if total == 0:
        return 0
    else:
        return float(target_total)/float(total)


q_label_good = []
for sentence in document.keys():
    frac = get_pct_of_sentence(document[sentence]['tokens'], "Q")
    sente = " ".join([i.raw for i in inf.doc.sentences[sentence].tokens])
    q_label_good.append((frac, sente))

q_label_good.sort(key=lambda x: x[0])

pdb.set_trace()

plt.scatter(range(0, len(z_flips_counts)), z_flips_counts)
plt.title('log z flips per iteration')
plt.ylabel('log z flips')
plt.ylabel('document iteration')
plt.show()
