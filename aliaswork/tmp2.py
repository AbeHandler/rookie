import pdb
import pickle
import os
from itertools import product
from rookie import log
from Levenshtein import distance
from itertools import product
from collections import defaultdict
from rookie.features import Featureizer
from rookie.utils import get_pickled

keys = [i.replace("\n", "") for i in open('keys.csv')]

levs = defaultdict(float)


def overlap(one, two):
    for pair in product(one.split(" "), two.split(" ")):
        if pair not in levs:
            levs[pair] = distance(pair[0], pair[1])
            if levs[pair] < 2:
                return True
    return False


if __name__ == "__main__":
    counter = 0
    total = float(sum(1 for x in product(keys, keys)))
    for key in product(keys, keys):
        counter = counter + 1
        if counter % 10000 == 0:
            pct = round(100 * (float(counter) / total), 2)
            log.info(pct)
        if key[0] == key[1]:
            pass
        else:
            if overlap(key[0], key[1]):
                print "'" + key[0] + "," + key[1] + "'"
