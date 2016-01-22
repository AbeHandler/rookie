import sys
import math
import pdb
from experiment.classes import IncomingFile


def query_unigram_overlap(sentence_tokens, query_words):
    return len(set(sentence_tokens).intersection(set(query_words)))


def get_snippet(query, docs):
    for doc in docs:
        get_snippet_doc(query, doc['fields']['text'])
    return "lorem ipsum, bro"


def get_snippet_doc(query, full_text):
    query_words = query.split(" ")
    sentences = full_text.split(".")
    potentials = []

    for i in range(0, len(sentences)):
        sentence = sentences[i]
        gram_overlap = query_unigram_overlap(sentence.split(" "), query_words)
        potentials.append((sentence, gram_overlap, i))

    max_overlap = max(potentials, key=lambda x: x[1])[1]

    potentials = [p for p in potentials if p[1] == max_overlap]

    winner = min(potentials, key=lambda x: x[2])

    return winner[0]


if __name__ == "__main__":
    file_name = sys.argv[1]
    query = sys.argv[2]
    inf = IncomingFile(file_name)
    full_text = inf.doc.full_text
