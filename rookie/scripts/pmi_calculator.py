import csv
import json
import pdb
from collections import defaultdict

pmis = defaultdict(list)

joint_counts = []
counts = []

TOTAL_PAIRS = 5799352.  # cat graph.csv | wc -l


def read_count_file(filename):
    output = []
    with open(filename, 'r') as countsfile:
        reader = csv.reader(countsfile, delimiter=',',
                            quotechar='"')
        for row in reader:
            output.append([i for i in row])
    return output


joint_counts = read_count_file("joint_counts.csv")
tmp_counts = read_count_file("counts.csv")

counts = {}

for item in tmp_counts:
    counts[item[0]] = float(item[1])

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
