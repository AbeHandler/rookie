import glob
import json
import csv
import itertools
import os
import pdb
import json
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

files_to_check = glob.glob(file_loc + "/*")

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
                gramner = sentence.gramners
                npe_product = set(itertools.product(gramner, gramner))
                stufffs = [i for i in npe_product]
                pairs = [NPEPair(i[0], i[1]) for i in npe_product]
                pairs = set(pairs)
                for pair in pairs:
                    npe_counts[repr(pair.word1)] += 1
                    npe_counts[repr(pair.word2)] += 1
                    instances[repr(pair.word1)].append((url, pair.word1.window, pubdate))
                    instances[repr(pair.word2)].append((url, pair.word2.window, pubdate))
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

for key in npe_counts.keys():
    temp = instances[key]
    instances_reduced[key] = tuple(set(temp))


json_dump(base + "instances.json", instances_reduced)
json_dump(base + "counts.json", npe_counts)
json_dump(base + "joint_counts.json", joint_counts)
