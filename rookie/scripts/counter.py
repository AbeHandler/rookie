'''
1. Counts occurances of types
2. Counts co-occurances of types
3. Tracks windows associated with cooccurances (instances)
'''

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
from rookie.classes import Document
from rookie import processed_location
from rookie.classes import NPEPair

counts = defaultdict(int)

joint_counts = defaultdict(int)

instances = defaultdict(list)

unigrams = defaultdict(int)

to_delete = ['joint_counts.json', 'instances.json', 'counts.json']


def attempt_delete(filename):
    try:
        os.remove(files_location + filename)
    except OSError:
        pass

for filename in to_delete:
    attempt_delete(filename)

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


class IncomingFile(object):
    """
    Mention of a ner or ngram
    Each mention is associated with coccurances
    """
    def __init__(self, filename):
        try:
            with (open(filename, "r")) as infile:
                self.doc = None
                json_in = json.loads(infile.read())
                self.url = json_in['url']
                self.pubdate = json_in['timestamp'].split(" ")[0]
                data = json_in['lines']
                self.doc = Document(data)
        except UnicodeEncodeError:
            pass
        except TypeError:
            pass
        except ValueError:
            pass


def process_sentence(infile, sentence):
    for token in sentence.tokens:
        unigrams[token.raw.upper()] += 1
    gramner = [i for i in get_gramner(sentence, True)]
    for gramne in gramner:
        counts[repr(gramne).upper()] += 1
    npe_product = set(itertools.product(gramner, gramner))
    npe_product = [i for i in npe_product if not i[0] == i[1]]
    pairs = [NPEPair(i[0], i[1]) for i in npe_product]
    for pair in pairs:
        assert pair.word1.window == pair.word2.window
        assert repr(pair.word1) in pair.word2.window
        assert repr(pair.word2) in pair.word1.window
        toappend = (infile.url, pair.word1.window,
                    infile.pubdate, sentence.sentence_no)
        key1 = (repr(pair.word1).upper(), repr(pair.word2).upper())
        key2 = (repr(pair.word2).upper(), repr(pair.word1).upper())
        instances[key1].append(toappend)
        instances[key2].append(toappend)
        jount_count_key = (repr(pair.word1).upper(), repr(pair.word2).upper())
        joint_counts[jount_count_key] += 1


def count_everything(files_to_check):
    counter = 0
    for filename in files_to_check:
        counter = counter + 1
        if counter % 100 == 0:
            print str(counter)
        infile = IncomingFile(filename)
        if infile.doc is None:
            pass
        else:
            for sentence in infile.doc.sentences:
                try:
                    process_sentence(infile, sentence)
                except UnicodeEncodeError:  # TODO: fix ascii error upstream
                    pass

count_everything(files_to_check)

# filter out strings that don't occur a lot
counts = dict((k, v) for k, v in counts.items() if v > 5)
joint_counts = dict((k, v) for k, v in joint_counts.items() if v > 5)
# unigrams = dict((k, v) for k, v in unigrams.items() if v > 5)


def reduce_instances(instances):
    instances_reduced = {}
    for key in joint_counts.keys():  # only need instances if joint count
        instances_reduced[key] = [i for i in set(instances[key])]
    return instances_reduced

# the BIG 5 MB instances dict can be reduced before the upcoming merges
instances = reduce_instances(instances)

pickle.dump(unigrams, open(files_location + "unigrams.p", "wb"))
pickle.dump(joint_counts, open(files_location + "joint_counts.p", "wb"))
pickle.dump(counts, open(files_location + "counts.p", "wb"))
pickle.dump(instances, open(files_location + "instances.p", "wb"))
