'''
#STEPS
1. Counts occurances of types
2. Counts co-occurances of types
3. Filter low counts
3. Find mergable keys
3. Merge the windows
4. Calculate PMIS
3. Creates some static files for the web application
'''

import glob
import json
import itertools
import sys
import os
import pickle
import re
import pdb
from jinja2 import Template
from collections import defaultdict
from rookie import files_location
from rookie.merger import Merger
from rookie import log
from rookie import window_length
from rookie.utils import time_stamp_to_date, get_gramner
from rookie.utils import stop_word
from rookie.classes import Document
from rookie import processed_location
from rookie.classes import NPEPair

npe_counts = defaultdict(int)

joint_counts = defaultdict(int)

instances = defaultdict(list)

base = files_location

to_delete = ['joint_counts.json', 'instances.json', 'counts.json']


def attempt_delete(filename):
    try:
        os.remove(base + filename)
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

counts = defaultdict(int)


def get_window(term, tmplist):
    tmplist.sort(key=lambda x: time_stamp_to_date(x[2]))
    outout = []
    for t in tmplist:
        try:
            index = t[1].index(term)
            left = t[1][:index][-window_length:]
            right = t[1][index + len(term):][:window_length]
            if len(left) == 0:
                left = "&nbsp;"
            if len(right) == 0:
                right = "&nbsp;"
            outout.append((t[2], left, term, right, t[0]))
        except ValueError:
            pass
    return outout


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
    gramner = [i for i in get_gramner(sentence, True)]
    for gramne in gramner:
        counts[repr(gramne)] += 1
    npe_product = set(itertools.product(gramner, gramner))
    npe_product = [i for i in npe_product if not i[0] == i[1]]
    pairs = set([NPEPair(i[0], i[1]) for i in npe_product])
    for pair in pairs:
        assert pair.word1.window == pair.word2.window
        assert repr(pair.word1) in pair.word2.window
        assert repr(pair.word2) in pair.word1.window
        toappend = (infile.url, pair.word1.window, infile.pubdate)
        instances[(repr(pair.word1), repr(pair.word2))].append(toappend)
        instances[(repr(pair.word2), repr(pair.word1))].append(toappend)
        jount_count_key = (repr(pair.word1), repr(pair.word2))
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


def reduce_instances(instances):
    instances_reduced = {}
    for key in joint_counts.keys():  # only need instances if joint count
        instances_reduced[key] = [i for i in set(instances[key])]
    return instances_reduced

# the BIG 5 MB instances dict can be reduced before the upcoming merges
instances = reduce_instances(instances)

pickle.dump(joint_counts, open(base + "joint_counts.p", "wb"))
pickle.dump(counts, open(base + "counts.p", "wb"))
pickle.dump(instances, open(base + "instances.p", "wb"))
