import pickle
import pdb
import json
from jinja2 import Template
from rookie.utils import time_stamp_to_date
from rookie.merger import Merger
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

# https://stackoverflow.com/questions/11458239/python-changing-value-in-a-tuple
def replace_tuple_val(tup, oldval, newval):
    lst = list(tup)
    for i in range(tup.count(oldval)):
        index = lst.index(oldval)
        lst[index] = newval
    return tuple(lst)


def merge_counts(key, big, small):
    try:
        counts[big] = counts[big] + counts[small]
    except KeyError:
        pass
    counts.pop(small, None)  # remove small from counts


def merge_joint_counts(key, big, small):
    to_replace = [i for i in joint_counts.keys() if small in i]
    for replace in to_replace:
        new_key = replace_tuple_val(replace, small, big)
        try:
            joint_counts[new_key] += joint_counts[replace]
        except KeyError:
            joint_counts[new_key] = joint_counts[replace]
        joint_counts.pop(replace, None)


def merge_instances(key, big, small):
    to_replace = [i for i in joint_counts.keys() if i[0] == small or i[1] == small]
    for replace in to_replace:
        new_key = replace_tuple_val(replace, small, big)
        # TODO replace mention in the text itself
        try:
            instances[new_key] += instances[replace]
        except KeyError:
            joint_counts[new_key] = joint_counts[replace]
    if small == "Baton Rouge Parish":
        pdb.set_trace()
    to_replace = [i for i in joint_counts.keys() if i[0] == small or i[1] == small]
    assert(len(to_replace) == 0)

merger = KeyMerge(counts.keys())  # TODO add levenshtein
#  pdb.set_trace()
for key in merger.get_keys_to_merge():
    big = max([key[0], key[1]], key=lambda x: len(x))
    small = min([key[0], key[1]], key=lambda x: len(x))
    keys = [i for i in joint_counts.keys() if small in i]
    log.info("merging {} into {}".format(small, big))
    if big[-1:] == "s":  # TODO move this logic into merger
        pass
    else:
        merge_counts(key, big, small)
        merge_joint_counts(key, big, small)
        merge_instances(key, big, small)
'''

'''
PMI Calculator
'''

pmis = defaultdict(list)

TOTAL_PAIRS = float(len(counts.keys()))

for joint_count in joint_counts.keys():
    word1 = joint_count[0]
    word2 = joint_count[1]
    pxy = float(joint_counts[joint_count]) / TOTAL_PAIRS
    px = float(counts[word1]) / TOTAL_PAIRS
    py = float(counts[word2]) / TOTAL_PAIRS
    pmi = pxy / (px * py)
    if pmi >= PMI_THRESHOLD:  # eyeballed to .5
        pmis[word1].append((word2, pmi))
        pmis[word2].append((word1, pmi))


def replace_index(position_replacing, old_keys, big, small):
    for lmention in old_keys:
        if position_replacing == 0:
            new_key = (big, lmention[1])
        else:
            new_key = (lmention[0], big)
        for mention in instances[lmention]:
            if big not in mention[1]:
                tmp = mention[1].replace(small, big)
                try:
                    assert big in tmp
                except AssertionError:
                    log.info(big)
                    log.info(tmp)
            else:
                tmp = mention[1]
            new_mention = (mention[0], tmp, mention[2])
            instances[new_key].append(new_mention)
        instances.pop(lmention, None)


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
    merged = Merger.merge_lists(pmireturns)
    merged = Merger.merge_lists(merged)
    # TODO this is not merging= windows in one pass
    merged = [i for i in merged if not i[0] == pmi]
    merged.sort(key=lambda x: x[1], reverse=True)
    if len(pmireturns) > 0:
        with (open("data/pmis/" + pmi + ".json", "w")) as jsonfile:
            json.dump(pmireturns, jsonfile)

    links = [i[0] for i in pmireturns if not i[0] == pmi]
    for hit in links:
        windows = [o for o in set(instances[(pmi, hit)])]
        windows = get_window(hit, windows)
        if len(windows) > 0:
            outfile = "data/windows/" + pmi + "###" + hit + ".json"
            with (open(outfile, "w")) as jsonfile:
                json.dump(windows, jsonfile)
