import pdb
import json
from collections import defaultdict

log = [i for i in open("run.log")]

vocabs = [o.replace("\n", "") for o in log if "DVOCAB" in o]

doc_vocabs = {}


def sentence_to_human(sentence):
    human = [(k, v) for k,v in sent_json.items()]
    human.sort(key=lambda x: int(x[0]))
    human = " ".join([o[1]['word'] for o in human])
    return human


for v in vocabs:
    vocab = json.loads(v.split("||")[2])
    filename = v.split("||")[1].split("//").pop()
    doc_vocabs[filename] = vocab

for doc_vocab in doc_vocabs:
    words = defaultdict(list)
    snapshots = [i.replace("\n", "").split("||").pop() for i in log if "sentence_snapshot" in i and filename in i]
    for s in snapshots:
        sentence = json.loads(s.split("||").pop().strip().strip("\n"))['tokens']
        for token_no in sentence.keys():
            words[sentence[token_no]['word']].append(sentence[token_no]['z'])


# find the sentences most responsive to the query

all_sentences = [i.replace("\n", "").split("||").pop() for i in log if "sentence_snapshot" in i]

sentence_scores = defaultdict(list)

'''
See which words are most associated with the query
'''

all_words = defaultdict(list)

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
See which sentenes are most associated with the query
'''

for sentence in sentence_scores:
    vals = sentence_scores[sentence]
    sentence_scores[sentence] = sum(vals) / float(len(vals))

scores = [(k, v) for k, v in sentence_scores.items()]

scores.sort(key=lambda x: x[1])

with open("sentences", "w") as outfile:
    for i in scores:
        outfile.write(str(i[1]) + "||" + i[0] + "||" + "\n")
