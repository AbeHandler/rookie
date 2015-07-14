import glob
import json
import itertools
import os
import pdb
import csv
import json
import pdb
from collections import defaultdict
from rookie import files_location
from rookie.merger import Merger

from rookie import log
from rookie import window_length
from rookie.utils import time_stamp_to_date
from rookie.classes import Document
from rookie import processed_location
from rookie.classes import NPEPair
from collections import defaultdict
from rookie import files_location

npe_counts = defaultdict(int)

joint_counts = defaultdict(int)

instances = defaultdict(list)

base = files_location

to_delete = 'joint_counts.json', 'instances.json', 'counts.json'


def get_window(term, tmplist):
    tmplist.sort(key=lambda x: time_stamp_to_date(x[2]))
    outout = []
    for t in tmplist:
        try:
            index = t[1].index(term)
            left = t[1][:index][-window_length:]
            right = t[1][index + len(term):][:window_length]
            outout.append((t[2], left, term, right, t[0]))
        except ValueError:
            pass
    return outout


def attempt_delete(filename):
    try:
        os.remove(base + filename)
    except OSError:
        pass


def json_dump(filename, defaultdict):
    with open(filename, 'w') as outfile:
        json.dump(dict(defaultdict), outfile)

for filename in to_delete:
    attempt_delete(filename)


file_loc = processed_location

files_to_check = glob.glob(file_loc + "/*")[0:10]

counter = 0


def stop_word(word):
    stops = ['U.S.', "|", "today",
             "Tuesday", "Wednesday",
             "Thursday", "Friday",
             "Saturday", "Sunday",
             "Monday"]
    if word in stops:
        return True
    return False

if __name__ == "__main__":
    for filename in files_to_check:
        try:
            counter = counter + 1
            if counter % 100 == 0:
                print str(counter)
            with (open(filename, "r")) as infile:
                json_in = json.loads(infile.read())
                url = json_in['url']
                pubdate = json_in['timestamp'].split(" ")[0]
                data = json_in['lines']
            doc = Document(data)
            sentences = doc.sentences
            sentence_counter = 0
            for sentence in sentences:
                sentence_counter = sentence_counter + 1
                gramner = sentence.gramners
                for gramne in gramner:
                    npe_counts[repr(gramne)] += 1
                    if repr(gramne) == "Strain.Marlin Peachey":
                        log.info(url)
                npe_product = set(itertools.product(gramner, gramner))
                stufffs = [i for i in npe_product]
                pairs = [NPEPair(i[0], i[1]) for i in npe_product]
                pairs = set(pairs)
                for pair in pairs:
                    if (stop_word(repr(pair.word1)) or
                       stop_word(repr(pair.word1))):
                        pass
                    else:
                        toappend = (url, pair.word1.window, pubdate)
                        instances[repr(pair.word1), repr(pair.word2)].append(toappend)
                        instances[repr(pair.word2), repr(pair.word1)].append((url, pair.word2.window, pubdate))
                        joint_counts[(repr(pair.word1) + "###" + repr(pair.word2))] += 1
        except UnicodeEncodeError:
            pass
        except KeyError:
            pass
        except TypeError:
            pass
        except ValueError:
            pass


npe_counts = dict((k, v) for k, v in npe_counts.items() if v > 5)
joint_counts = dict((k, v) for k, v in joint_counts.items() if v > 5)

# instances_reduced = {}

# for key in npe_counts.keys():
#    temp = set(instances[key])
#    temp = [p for p in temp]
#    temp = get_window(key, temp)
#    instances_reduced[key] = tuple(set(temp))
# json_dump(base + "instances.json", instances_reduced)


#  writing to file because need these static files
json_dump(base + "counts.json", npe_counts)
json_dump(base + "joint_counts.json", joint_counts)
with open(base + "keys.csv", "w") as outfile:
    for key in npe_counts.keys():
        outfile.write(key + "\n")


'''
PMI Calculator
'''

pmis = defaultdict(list)

joint_counts = []
counts = []


def read_count_file(jsonfile):
    with open(jsonfile) as infile:
        data = json.load(infile)
    return data


joint_counts = read_count_file(files_location + "joint_counts.json")
counts = read_count_file(files_location + "counts.json")

counts = dict((k, float(v)) for k, v in counts.items())

TOTAL_PAIRS = len(counts.keys())

for joint_count in joint_counts.keys():
    word1 = joint_count.split("###")[0]
    word2 = joint_count.split("###")[1]
    pxy = float(joint_counts[joint_count]) / TOTAL_PAIRS
    px = counts[word1] / TOTAL_PAIRS
    py = counts[word2] / TOTAL_PAIRS
    pmi = pxy / (px * py)
    pmis[word1].append((word2, pmi))
    pmis[word2].append((word1, pmi))

for pmi in pmis:
    with (open("data/pmis/" + pmi + ".json", "w")) as jsonfile:
        hits = pmis[pmi].sort(key=lambda x: x[1])
        for hit in hits:
            merged = [o for o in set(instances[pmi, 'story Report'])]
            merged = Merger.merge_lists(merged)
            merged = Merger.merge_lists(merged)
            # TODO this is not merging windows
            merged = [i for i in merged if not i[0] == pmi]
            pdb.set_trace()
            if len(merged) > 0:
                json.dump(merged, jsonfile)
