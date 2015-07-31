import pickle
import itertools
import pdb
import collections
from Levenshtein import distance
from rookie.experiment.simplemerger import Merger
from collections import defaultdict


results = pickle.load(open("mitch.p"))
results = pickle.load(open("gusman.p"))

people = [r['fields']['people'] for r in results if 'people' in r['fields'].keys()]
people = list(itertools.chain.from_iterable(people))
people = collections.Counter(people).most_common(100)
names = [[o[0]] for o in people]
names = Merger.merge_lists(names)

mergers = [n for n in names if len(n) > 1]


def get_jaccard(one, two):
    one = set(one.split(" "))
    two = set(two.split(" "))
    jacard = float(len(one & two)) / len(one | two)
    return jacard


def get_representitive_item(aliases, kind_of_item=None):
    items = [(i[0], i[1], get_jaccard(i[0], i[1])) for i in itertools.product(aliases, aliases) if i[0] != i[1]]
    scores = defaultdict(float)
    for i in items:
        scores[i[0]] += i[2]
    scores = [(k, v) for k, v in scores.items()]
    if kind_of_item == "people" or kind_of_item == "organizations":
        max_jac = max(o[1] for o in scores)
        scores = [o for o in scores if o[1] == max_jac]  # first filter by jacd
        max_len = max(len(o[0].split(" ")) for o in scores)
        scores = [o for o in scores if len(o[0].split(" ")) == max_len]

    # This is a correction for cases where you end up with Bob Jame and Bob James (i.e. possessive)
    if kind_of_item == "people" and len(scores) == 2 and distance(scores[0][0], scores[1][0]) == 1:
        if scores[0][0][-1:].upper() == "S":
            return scores[1]
        if scores[1][0][-1:].upper() == "S":
            return scores[0]

    return scores.pop()
'''
    scores.sort(key=lambda x: x[1])
    print scores
    scores = scores[-2:]
    if distance(scores[0][0], scores[1][0]) == 1 \
       and (scores[0][0][-1:] == "s" or scores[1][0][-1:].upper() == "S"):
            print min(scores[-3:], key=lambda x: x[0])
    else:
        print max(scores[-3:], key=lambda x: x[1])
'''

for m in mergers:
    print get_representitive_item(m, "people")
