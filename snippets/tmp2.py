import pdb
import pickle
import random
import math
import itertools
import numpy as np
import matplotlib.pyplot as plt
import pickle
from collections import Counter
from rookie.classes import IncomingFile

unigram_counts = pickle.load(open("pickled/unigram_df.p", "r"))

'''
Load the precomputed corpus language model
'''

corpus_lm = pickle.load(open("snippets/lm.p", "rb"))

vocab = corpus_lm.keys()

'''
Load the sample file and query
'''

file_loc = "/Users/abramhandler/research/rookie/data/lens_processed/"
fn = "31ec3ae1df97f31f889d90e973934d3ee02e88c034672c14cd4e54af"
inf = IncomingFile(file_loc + fn)

query = ["orleans", "parish", "prison", "vera", "institute"]

sources = ['G', 'Q', 'D']  # potential values for d

'''
Find the document's vocabulary
'''

all_tokens = [i.tokens for i in inf.doc.sentences]
doc_vocab = [o.raw.lower() for o in list(itertools.chain(*all_tokens))]
doc_vocab_counter = Counter(doc_vocab)  # count of each word in doc
doc_vocab = [i for i in set(doc_vocab)]


'''
Setup pseudocounts and counts for doc/query LMs + sentence distributions.
'''
query_pseudoc = {}
query_lm_counts = {}
for word in doc_vocab:
    query_pseudoc[word] = 5
    query_lm_counts[word] = 0

doc_pseudoc = {}
doc_lm_counts = {}
for word in doc_vocab:
    doc_pseudoc[word] = 5
    doc_lm_counts[word] = 0

pi_pseudo_counts = {'D': 4, 'Q': 4, 'G': 4}

lms = {}
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


def lookup_p_lms(counts, pseudocounts):
    denom = sum(v for k, v in counts.items())
    denom = denom + sum(v for k, v in pseudocounts.items())
    output = {}
    output['Q'] = float((counts['Q'] + pseudocounts['Q'])) / denom
    output['G'] = float((counts['G'] + pseudocounts['G'])) / denom
    output['D'] = float((counts['D'] + pseudocounts['D'])) / denom
    return output


def flip_for_z(p_tokens, p_lms, token):
    if token in query:
        return "Q"
    total = 0.
    ranges = {}
    for source in sources:
        old_total = total
        source_area = p_tokens[source] * p_lms[source]
        new_total = total + source_area
        ranges[source] = (old_total, new_total)
        total = new_total
    flip = random.uniform(0, total)
    for i in ranges.keys():
        win_zone = ranges[i]
        if flip >= win_zone[0] and flip <= win_zone[1]:
            return i


def flip_for_pi_count(pi_pseudo_c, sentence):
    denom = sum(v for k, v in pi_pseudo_c.items())
    denom = float(denom + sum(v for k, v in sentence['pi_counts'].items()))
    total = 0.
    ranges = {}
    tokens = sentence['tokens']
    for source in sources:
        old_total = total
        p_counts = (pi_pseudo_c[source] + sentence['pi_counts'][source])/denom
        z_count_source = len([i for i in tokens if tokens[i]['z'] == source])
        p_zs = float(z_count_source) / float(len(tokens))
        source_area = p_zs * p_counts
        new_total = total + source_area
        ranges[source] = (old_total, new_total)
        total = new_total
    flip = random.uniform(0, total)
    for i in ranges.keys():
        win_zone = ranges[i]
        if flip >= win_zone[0] and flip <= win_zone[1]:
            return i

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

iterations = 100

z_flips_counts = []
grand_total_score_keeping = []

for i in range(0, iterations):
    print i
    z_flips_this_iteration = 0
    for sentence in document.keys():
        pi_counts = document[sentence]['pi_counts']
        for token_no in document[sentence]['tokens']:
            token = document[sentence]['tokens'][token_no]
            p_tokens = {}
            p_tokens['G'] = corpus_lm[token['word']]
            p_tokens['Q'] = lookup_p_token(token['word'], 'Q')
            p_tokens['D'] = lookup_p_token(token['word'], 'D')
            p_lms = lookup_p_lms(pi_counts, pi_pseudo_counts)
            old_z = token['z']
            new_z = flip_for_z(p_tokens, p_lms, token['word'])
            if old_z != new_z:
                z_flips_this_iteration += 1
            document[sentence]['tokens'][token_no]['z'] = new_z
            if new_z != "G":  # general LM is fixed
                lms[new_z]['counts'][token['word']] += 1
        pi_count = flip_for_pi_count(pi_pseudo_counts, document[sentence])
        # increment the pi counts
        document[sentence]['pi_counts'][pi_count] += 1

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
    grand_total_score_keeping.append(score_keeping)
    z_flips_counts.append(math.log(z_flips_this_iteration))


'''
Score keeping and debugging
'''

most_common_labeled_q = []
joined = [i for i in itertools.chain(*grand_total_score_keeping)]
for word in doc_vocab_counter:
    tmp = [o for o in joined if o[0] == word]
    total_occurances = float(sum(i[1] for i in tmp))
    total_occurances_zs = float(sum(i[2] for i in tmp))
    if total_occurances_zs == 0:
        most_common_labeled_q.append((word, 0))
    else:
        most_common_labeled_q.append((word, total_occurances_zs/total_occurances))

q_label_good = []
for sentence in document.keys():
    pi_counts = document[sentence]['pi_counts']
    tokens = document[sentence]['tokens']
    sente = ""
    for key in tokens.keys():
        sente = sente + " " + tokens[key]['word']
    tot_query = float(sum(v for k, v in pi_counts.items() if k == "Q"))
    tot_counts = float(sum(v for k, v in pi_counts.items()))
    pct_pi_counts = tot_query / tot_counts
    q_label_good.append((pct_pi_counts, sente))

q_label_good.sort(key=lambda x: x[0])

pdb.set_trace()

plt.scatter(range(0, len(z_flips_counts)), z_flips_counts)
plt.title('log z flips per iteration')
plt.ylabel('log z flips')
plt.ylabel('document iteration')
plt.show()
