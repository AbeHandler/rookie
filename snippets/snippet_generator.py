import sys
import math
from rookie.classes import IncomingFile

file_name = sys.argv[1]

query = sys.argv[2]

query_words = query.split(" ")

inf = IncomingFile(file_name)

full_text = inf.doc.full_text

sentences = full_text.split(".")


def query_unigram_overlap(sentence_tokens, query_words):
    return len(set(sentence_tokens).intersection(set(query_words)))

potentials = []

for i in range(0, len(sentences)):
    sentence = sentences[i]
    gram_overlap = query_unigram_overlap(sentence.split(" "), query_words)
    potentials.append((sentence, gram_overlap, i))

max_overlap = max(potentials, key=lambda x: x[1])[1]

potentials = [p for p in potentials if p[1] == max_overlap]

print min(potentials, key=lambda x: x[2])
