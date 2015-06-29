import json
import collections
import pickle
import pdb
from rookie.classes import Coreferences
from rookie.classes import Document
from rookie.classes import Window
from rookie.classes import N_Grammer
import glob

ner_grams = {}

file_loc = "/Users/abramhandler/research/rookie/data/lens_processed/*"

files_to_check = glob.glob(file_loc)


def add_grams_to_dict(ner, grams):
    if ner in ner_grams.keys():
        temp = ner_grams[ner]
        temp = temp + grams
        ner_grams[ner] = temp
    else:
        ner_grams[ner] = grams


def grams_to_list(grams):
    grams_list = []
    for ngram in grams:
        raw = " ".join(tok.raw for tok in ngram)
        grams_list.append(raw)
    return grams_list


def filter_counter_to_bigger_than_one(counter):
    out = []
    for key in counter.keys():
        if counter[key] > 1:
            out.append((key, counter[key]))
    return out


def get_grams(fn):
    with open(fn, "r") as to_read:
        py_wrapper_output = json.loads(to_read.read())['lines']
        doc = Document(py_wrapper_output)
        ng = N_Grammer()
        ngrams = ng.get_syntactic_ngrams(doc.tokens)
        bigrams = ngrams[0]
        trigrams = ngrams[1]
        grams = bigrams + trigrams
        for gram in grams:
            sentence = doc.sentences[gram[0].sentence_no]
            window = Window.get_window(sentence, gram)
            window_grams = ng.get_syntactic_ngrams(window)
            bigrams = window_grams[0]
            trigrams = window_grams[1]
            ngram_key = " ".join([n.raw for n in gram])
            add_grams_to_dict(ngram_key, bigrams)
            add_grams_to_dict(ngram_key, trigrams)


if __name__ == "__main__":
    counter = 0
    final_output = {}
    for f in files_to_check:
        try:
            get_grams(f)
            counter = counter + 1
            print counter
        except ValueError:
            pass
        except KeyError:
            pass
        except TypeError:
            pass
    pickle.dump(ner_grams, open("data/tmp_grams.p", "wb"))

    for key in ner_grams.keys():
        grams = [i for i in ner_grams[key]]
        grams_list = grams_to_list(grams)
        counter = collections.Counter(grams_list)
        filtered = filter_counter_to_bigger_than_one(counter)
        final_output[key] = filtered

    pickle.dump(final_output, open("data/window_grams.p", "wb"))
