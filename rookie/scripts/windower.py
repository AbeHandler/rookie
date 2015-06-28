import json
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


def get_grams(fn):
    with open(fn, "r") as to_read:
        py_wrapper_output = json.loads(to_read.read())['lines']
        corefs = Coreferences(py_wrapper_output)
        doc = Document(py_wrapper_output, corefs)
        for sentence in doc.sentences:
            for ner in sentence.ner:
                window = Window.get_window(sentence, ner, 10)
                ng = N_Grammer()
                grams = ng.get_syntactic_ngrams(window)
                bigrams = grams[0]
                trigrams = grams[1]
                add_grams_to_dict(ner, bigrams)
                add_grams_to_dict(ner, trigrams)

counter = 0
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

pickle.dump(ner_grams, open("data/window.p", "wb"))
