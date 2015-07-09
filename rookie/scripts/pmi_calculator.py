import csv
import json
import pdb
from collections import defaultdict
from rookie import files_location

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

with (open("pmis.json", "w")) as jsonfile:
    json.dump(pmis, jsonfile)
