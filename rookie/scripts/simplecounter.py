'''
1. Counts occurances of types
2. Counts co-occurances of types
3. Tracks windows associated with cooccurances (instances)
'''
import collections
import glob
import json
import itertools
import sys
import os
import pdb
import pickle
from collections import defaultdict
from rookie import files_location
from rookie import log
from rookie.utils import get_gramner
from rookie.classes import Document, IncomingFile
from rookie import processed_location
from rookie.classes import NPEPair

counts = defaultdict(int)

types = defaultdict(list)

try:
    limit = int(sys.argv[1])
    files_to_check = glob.glob(processed_location + "/*")[0:limit]
except TypeError:
    files_to_check = glob.glob(processed_location + "/*")
except IndexError:
    files_to_check = glob.glob(processed_location + "/*")


def json_dump(filename, defaultdict):
    with open(filename, 'w') as outfile:
        json.dump(dict(defaultdict), outfile)


def process_sentence(infile, sentence):
    gramner = [i for i in get_gramner(sentence, True)]
    for gramne in gramner:
        types[repr(gramne).upper()].append(gramne.type)
        counts[repr(gramne).upper()] += 1


def count_everything(files_to_check):
    counter = 0
    for filename in files_to_check:
        counter = counter + 1
        if counter % 100 == 0:
            print str(counter)
        infile = IncomingFile(filename)
        if infile.doc is None:
            print "failure {}".format(filename)
        else:
            for sentence in infile.doc.sentences:
                try:
                    process_sentence(infile, sentence)
                except UnicodeEncodeError:  # TODO: fix ascii error upstream
                    pass

count_everything(files_to_check)

# filter out strings that don't occur a lot
counts = dict((k, v) for k, v in counts.items() if v > 5)
types = dict((k, collections.Counter(v)) for k, v in types.items() if len(v) > 5)
# unigrams = dict((k, v) for k, v in unigrams.items() if v > 5)

pickle.dump(counts, open(files_location + "counts.p", "wb"))
pickle.dump(types, open(files_location + "types.p", "wb"))
