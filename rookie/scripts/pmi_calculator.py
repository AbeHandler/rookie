import csv
import json
import pdb
from collections import defaultdict
from rookie import files_location
from rookie.merger import Merger

pmis = defaultdict(list)

joint_counts = []
counts = []


def read_count_file(jsonfile):
    with open(jsonfile) as infile:
        data = json.load(infile)
    return data

instances = read_count_file(files_location + "instances.json")
joint_counts = read_count_file(files_location + "joint_counts.json")
counts = read_count_file(files_location + "counts.json")

counts = dict((k, float(v)) for k, v in counts.items())

TOTAL_PAIRS = len(instances.keys())

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
        pmis[pmi].sort(key=lambda x: x[1])
        merged = Merger.merge_lists(pmis[pmi])
        merged = Merger.merge_lists(merged)
        # TODO this is not merging windows
        merged = [i for i in merged if not i[0] == pmi]
        if len(merged) > 0:
            json.dump(merged, jsonfile)
