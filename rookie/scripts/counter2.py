import pickle
import pdb
import json
from rookie.utils import calculate_pmi
from jinja2 import Template
from rookie.utils import time_stamp_to_date
from rookie import log
from rookie import window_length
from collections import defaultdict
from rookie import PMI_THRESHOLD
from rookie import files_location
from rookie.pmismerger import KeyMerge  # this one merges based on jacaard

counts = pickle.load(open("counts.p", "rb"))
joint_counts = pickle.load(open("joint_counts.p", "rb"))
instances = pickle.load(open("instances.p", "rb"))
base = files_location


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

'''
PMI Calculator
'''

pmis = defaultdict(list)

TOTAL_PAIRS = float(len(counts.keys()))

for joint_count in joint_counts.keys():
    pmi = calculate_pmi(joint_count[0], joint_count[1], counts, joint_counts)
    if pmi >= PMI_THRESHOLD:  # eyeballed to .5
        pmis[joint_count[0]].append((joint_count[1], pmi))
        pmis[joint_count[1]].append((joint_count[0], pmi))


with open(base + "keys.csv", "w") as outfile:
    for key in counts.keys():
        outfile.write(key + "\n")


with open(base + "searchbar.html", "w") as outfile:
    template = Template('<option value="{{key}}">{{key}}</option>')
    for term in counts.keys():
        outfile.write(template.render(key=term) + "\n")

'''
PMI Calculator
'''

joint_counts = []
counts = []

for pmi in pmis:
    pmireturns = [o for o in set(pmis[pmi])]
    # merged = Merger.merge_lists(pmireturns)
    # merged = Merger.merge_lists(merged)
    # TODO this is not merging= windows in one pass
    # merged = [i for i in merged if not i[0] == pmi]
    # merged.sort(key=lambda x: x[1], reverse=True)
    if len(pmireturns) > 0:
        try:
            with (open("data/pmis/" + pmi + ".json", "w")) as jsonfile:
                json.dump(pmireturns, jsonfile)
        except IOError:
            pass

    links = [i[0] for i in pmireturns]
    for hit in links:
        windows = [o for o in set(instances[(pmi, hit)])]
        windows = get_window(hit, windows)
        if len(windows) > 0:
            try:
                outfile = "data/windows/" + pmi + "###" + hit + ".json"
                with (open(outfile, "w")) as jsonfile:
                    json.dump(windows, jsonfile)
            except IOError:
                pass
