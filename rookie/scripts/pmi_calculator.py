import csv
import json
import pdb
from collections import defaultdict
from rookie import files_location

pmis = defaultdict(list)

joint_counts = []
counts = []

TOTAL_PAIRS = 5799352.  # cat graph.csv | wc -l


def read_count_file(jsonfile):
    with open(jsonfile) as infile:
        data = json.load(infile)
    return data

joint_counts = read_count_file(files_location + "joint_counts.json")
counts = read_count_file(files_location + "counts.json")

counts = dict((k, float(v)) for k, v in counts.items())

for joint_count in joint_counts:
    word1 = joint_count[0]
    word2 = joint_count[1]
    pxy = float(joint_count[2]) / TOTAL_PAIRS
    px = counts[word1] / TOTAL_PAIRS
    py = counts[word2] / TOTAL_PAIRS
    pmi = pxy / (px * py)
    pmis[word1].append((word2, pmi))
    pmis[word2].append((word1, pmi))

with (open("pmis.json", "w")) as jsonfile:
    json.dump(pmis, jsonfile)
