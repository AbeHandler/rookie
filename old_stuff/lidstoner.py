'''
This calcluates probability ratios for given terms
'''


import pickle
import itertools
import math
import pdb
import re
from collections import defaultdict
from rookie.pmismerger import KeyMerge

keys = [i.replace("\n", "").split(' ') for i in open('keys.csv')]
keys_temp = reduce(lambda x, y: x+y, keys)
keys_unigrams = [i for i in set(keys_temp)]
counts = pickle.load(open("counts.p", "rb"))
unigrams = pickle.load(open("unigrams.p", "rb"))

keys_unigrams = ['Landrieu']

LAMBDA = .5

COUNT_VOCAB = len(unigrams.keys())


alias_potentials = defaultdict(list)


def get_count(term):
    try:
        return counts[term]
    except KeyError:
        return unigrams[term]


def Lidstone(count_potential, count_given):
    num = float(count_potential + LAMBDA)
    denom = float(count_given + (COUNT_VOCAB * LAMBDA))
    return num / denom

# just focus on difference of 1
for key in keys_unigrams:
    potential_overlaps = [" ".join(i) for i in keys if key in i]
    for a in itertools.product(potential_overlaps, potential_overlaps):
        count_one = float(get_count(a[0]))
        count_two = float(get_count(a[1]))
        len_dif = math.fabs(len(a[1].split(" ")) - len(a[0].split(" ")))
        if len_dif == 1 and ((a[0] in a[1]) or (a[1] in a[0])):
            small = min(a, key=lambda x: len(x.split(" ")))
            big = max(a, key=lambda x: len(x.split(" ")))
            given = re.findall(small, big)[0]
            potential = big.replace(given, "").strip()
            potential = re.sub(' +', ' ', potential)
            tmp = (big, Lidstone(get_count(potential), get_count(given)))
            alias_potentials[small].append(tmp)

for key in alias_potentials.keys():
    print key
    alias_potentials[key].sort(key=lambda x: x[1])
    print alias_potentials[key]
