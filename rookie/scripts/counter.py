'''
1. Counts occurances of types
2. Counts co-occurances of types
3. Creates some static files for the web application
'''
import glob
import json
import itertools
import os
import pdb
from jinja2 import Template
from rookie import PMI_THRESHOLD
from collections import defaultdict
from rookie import files_location
from rookie.merger import Merger
from rookie import log
from rookie import window_length
from rookie.utils import time_stamp_to_date
from rookie.utils import stop_word
from rookie.classes import Document
from rookie import processed_location
from rookie.classes import NPEPair

npe_counts = defaultdict(int)

joint_counts = defaultdict(int)

instances = defaultdict(list)

base = files_location

to_delete = 'joint_counts.json', 'instances.json', 'counts.json'

file_loc = processed_location

files_to_check = glob.glob(file_loc + "/*")


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

counter = 0


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
                gramner = [i for i in sentence.gramners if not stop_word(repr(i))]
                for gramne in gramner:
                    npe_counts[repr(gramne)] += 1
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

instances_reduced = {}

instances_print = {}
for key in instances.keys():
    nkey = "###".join([o for o in key])
    instances_reduced[nkey] = instances[key]

json_dump(base + "instances.json", instances_reduced)

'''
for key in npe_counts.keys():
    temp = set(instances[key])
    temp = [p for p in temp]
    temp = get_window(key, temp)
    instances_reduced[key] = tuple(set(temp))
json_dump(base + "instances.json", instances_reduced)
'''

json_dump(base + "counts.json", npe_counts)
json_dump(base + "joint_counts.json", joint_counts)
with open(base + "keys.csv", "w") as outfile:
    for key in npe_counts.keys():
        outfile.write(key + "\n")


with open(base + "searchbar.html", "w") as outfile:
    template = Template('<option value="{{key}}">{{key}}</option>')
    for term in npe_counts.keys():
        outfile.write(template.render(key=term) + "\n")


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
    if pmi >= PMI_THRESHOLD:  # eyeballed to .5
        pmis[word1].append((word2, pmi))
        pmis[word2].append((word1, pmi))

for pmi in pmis:
    pmireturns = [o for o in set(pmis[pmi])]
    merged = Merger.merge_lists(pmireturns)
    merged = Merger.merge_lists(merged)
    # TODO this is not merging windows in one pass
    merged = [i for i in merged if not i[0] == pmi]
    merged.sort(key=lambda x: x[1], reverse=True)
    if len(merged) > 0:
        with (open("data/pmis/" + pmi + ".json", "w")) as jsonfile:
            json.dump(merged, jsonfile)

    links = [i[0] for i in merged]
    for hit in links:
        windows = [o for o in set(instances[pmi, hit])]
        windows = get_window(hit, windows)
        if len(windows) > 0:
            outfile = "data/windows/" + pmi + "###" + hit + ".json"
            with (open(outfile, "w")) as jsonfile:
                json.dump(windows, jsonfile)
