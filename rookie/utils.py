import string
import json
import re
import datetime
import itertools
import pickle
import pdb
# from rookie.classes import NPEPair, Gramner
# from rookie import files_location
from pylru import lrudecorator


class Result(object):

    def __init__(self, string, pmi, windows):
        '''
        Initialize w/ the json output
        '''
        self.string = string
        self.pmi = pmi
        self.windows = windows
        self.id = string.__hash__()  # get ID from use in template

    def __repr__(self):
            return string

'''
def calculate_pmi(term1, term2, counts, joint_counts):
    try:
        TOTAL_PAIRS = float(len(counts.keys()))
        pxy = float(joint_counts[(term1, term2)] + 1) / TOTAL_PAIRS
        px = float(counts[term1] + 1) / TOTAL_PAIRS
        py = float(counts[term2] + 1) / TOTAL_PAIRS
        pmi = pxy / (px * py)
        return pmi
    except KeyError:
        log.info(term1 + "," + term2)
        return 0
'''


def get_jaccard(one, two):
    one = set(one.split(" "))
    two = set(two.split(" "))
    jacard = float(len(one & two)) / len(one | two)
    return jacard

'''
def dedupe_people(ner):
    Remove cases where there are two mentions of a person ner
    in a group of entities. Assume coreference. Delete the shorter one
    Ex. "Clinton" and "Bill Clinton"
    if len(ner) == 0:
        return ner
    tner = ner
    people = [i for i in tner if i.type == "PERSON"]
    npe_product = set(itertools.product(people, people))
    npe_product = [i for i in npe_product if not i[0] == i[1]]
    pairs = [NPEPair(repr(i[0]), repr(i[1])) for i in npe_product]
    pairs = set(pairs)
    for i in pairs:
        if i.word1 in i.word2:
            try:
                delete_this = min([i.word1, i.word2], key=lambda x: len(repr(x)))
                tner.remove([i for i in ner if repr(i) == delete_this][0])
            except IndexError:
                pass  # sometimes earlier iterations of loop already got it
    return tner
'''

def get_gramner(sentence, exclude_stop_words):
        grams = sentence.ngrams  # returns bigrams/trigrams
        gramners = []
        for gram in grams:
            window = sentence.tokens  # the window = tokens in the sentence
            gramner = Gramner(gram, window, "ngram")
            gramners.append(gramner)
        for ne in dedupe_people(sentence.ner):
            window = sentence.tokens  # the window = tokens in the sentence
            gramner = Gramner(ne.tokens, window, ne.type)
            gramners.append(gramner)
        if exclude_stop_words:
            return [i for i in gramners if not stop_word(repr(i))]
        else:
            return gramners


@lrudecorator(100)
def get_pickled(file):
    return pickle.load(open(file, "rb"))


@lrudecorator(100)
def get_stopwords():
    stopwords = [i.replace("\n", "") for i in open("stopwords.txt")]
    return stopwords


def stop_word(word):
    stops = get_stopwords()
    if word in stops:
        return True
    return False


@lrudecorator(100)
def get_pmi():
    with (open(files_location + "pmis.json", "r")) as rw:
        pmis = json.load(rw)
        for key in pmis:
            pmis[key].sort(key=lambda x: x[1], reverse=True)
    return pmis


@lrudecorator(100)
def clean_whitespace(full_text):
    pattern = re.compile("\ {2,}")  # clean any big spaces left over
    full_text = pattern.sub(" ", full_text)  # replace w/ small spaces
    return full_text


@lrudecorator(100)
def time_stamp_to_date(timestamp):
    # example: 2011-01-10
    yr = int(timestamp.split("-")[0])
    mo = int(timestamp.split("-")[1])
    dy = int(timestamp.split("-")[2])
    return datetime.date(yr, mo, dy)


@lrudecorator(100)
def clean_punctuation(input_string):
    '''
    Assumes ASCII input. TODO: Error handling.
    '''
    for punctuation in string.punctuation:
        input_string = input_string.replace(punctuation, " ")
    return input_string


@lrudecorator(100)
def get_document_frequencies(freq_type):
    return get_pickled(files_location + "pickled/df_" + freq_type + ".p")


def compress_sentence(sentence):
    deps = sentence.deps
    return "Wowza"
