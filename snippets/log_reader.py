import pdb
import os
import json
import matplotlib.pyplot as plt
from collections import defaultdict


def sentence_to_human(sentence):
    '''
    json to person translation
    '''
    human = [(k, v) for k, v in sent_json.items()]
    human.sort(key=lambda x: int(x[0]))
    human = " ".join([o[1]['word'] for o in human])
    return human


'''
Check the per document vocabs to see if it associates
the right words with documents vs general
'''

if os.path.isfile("most_general_words"):
    os.remove("most_general_words")

log = [i for i in open("run.log")]

vocabs = [o.replace("\n", "") for o in log if "DVOCAB" in o]

doc_vocabs_original = {}

for v in vocabs:
    vocab = json.loads(v.split("||")[2])
    filename = v.split("||")[1].split("//").pop()
    doc_vocabs_original[filename] = vocab

for doc_vocab in doc_vocabs_original:
    words = defaultdict(list)
    snapshots = [i.replace("\n", "").split("||").pop()
                 for i in log if "sentence_snapshot" in i and filename in i]
    for s in snapshots:
        sentence = json.loads(s.split("||").pop().strip().strip("\n"))
        sentence = sentence['tokens']
        for token_no in sentence.keys():
            words[sentence[token_no]['word']].append(sentence[token_no]['z'])
    for word in words.keys():
        denom = sum(1. for i in words[word])
        word_pcts = {}
        for source in ['D', 'G', 'Q']:
            num = sum(1. for i in words[word] if i == source)
            word_pcts[source] = num/denom
        words[word] = word_pcts
    words = [(k, v) for k, v in words.items()]
    pct_general = [(i[0], i[1]['G']) for i in words]
    pct_general.sort(key=lambda x: x[1])
    with open("most_general_words", "a") as outfile:
        outfile.write(doc_vocab + ":")
        for i in pct_general:
            outfile.write(i[0] + "," + str(i[1]))
        outfile.write("\n")

'''
See which words are most associated with the query
'''

sentence_scores = defaultdict(list)

all_words = defaultdict(list)

all_sentences = [i.replace("\n", "").split("||").pop() for i in log if "sentence_snapshot" in i]

for sentence in all_sentences:
    sent_json = json.loads(sentence.replace("\n", ""))['tokens']
    total_tokens = float(len(sent_json))
    total_q = float(len([v['z'] for k, v in sent_json.items() if v['z'] == "Q"]))
    frac = total_q/total_tokens
    sentence_scores[sentence_to_human(sentence)].append(frac)
    for token in sent_json:
        all_words[sent_json[token]['word']].append(sent_json[token]['z'])

rr = [(k, v) for k, v in all_words.items()]

word_scores = []

for item in rr:
    denom = float(sum(1 for i in item[1]))
    num = float(sum(1 for i in item[1] if i == "Q"))
    if denom == 0:
        word_scores.append((item[0], 0))
    else:
        word_scores.append((item[0], num/denom))

word_scores.sort(key=lambda x: x[1])

with open("qwords", "w") as outfile:
    for i in word_scores:
        outfile.write(i[0] + "||" + str(i[1]) + "\n")


'''
See which sentences are most associated with the query
'''

all_sentences = [i.replace("\n", "").split("||").pop() for i in log if "sentence_snapshot" in i]

sentence_scores = defaultdict(list)

for sentence in sentence_scores:
    vals = sentence_scores[sentence]
    sentence_scores[sentence] = sum(vals) / float(len(vals))

scores = [(k, v) for k, v in sentence_scores.items()]

scores.sort(key=lambda x: x[1])

with open("sentences", "w") as outfile:
    for i in scores:
        outfile.write(str(i[1]) + "||" + i[0] + "||" + "\n")


'''
check z flips for convergence
'''
log = [i for i in open("run.log")]
z_flips = [i.replace("\n", "").split("||")[1:3] for i in log if "zflips" in i]

plt.scatter([int(i[0]) for i in z_flips], [int(i[1]) for i in z_flips])
plt.title('sum z flips by iteration: all docs')
plt.ylabel('# z flips')
plt.xlabel('iteration')
plt.savefig("test.png")
