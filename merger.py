import json
import itertools
import pdb
import math
from rookie.classes import NPEPair
from Levenshtein import distance


def split_list(input_list):
    half = len(input_list)/2
    return input_list[:half], input_list[half:]


with (open("pmis.json", "r")) as rw:
    pmis = json.load(rw)
    for key in pmis:
        pmis[key].sort(key=lambda x: x[1], reverse=True)


def get_jaccard(one, two):
    one = set(one.split(" "))
    two = set(two.split(" "))
    jacard = float(len(one & two)) / len(one | two)
    return jacard


def is_same(one, two):
    if distance(one, two) < 2:
        return True
    if math.fabs(len(one.split(" ")) - len(two.split(" "))) == 1:
        lesser = min(one, two, key=lambda x: len(x.split(" ")))
        lesser = [i for i in lesser.split(" ")]
        greater = max(one, two, key=lambda x: len(x.split(" ")))
        greater = [i for i in greater.split(" ")]

        # lesser is a subset of greater...
        # i.e. "Mary Landrieu" is subset of "Sen. Mary Landrieu"
        if set(lesser) < set(greater):
            return True
        else:
            return False
    if get_jaccard(one, two) >= .5:
        return True
    else:
        return False


def merge_candidates(candidates):
    '''
    Sample imput
    ([u'Jon Doe', 31.086], [u'Jon Moe', 30.08])
    '''
    out = []
    for c in candidates:
        item1 = c[0]
        item2 = c[1]
        # pick the longer one for string value
        string_value = max(item1[0], item2[0], key=lambda x: len(x))
        pmi_value = (item1[1] + item2[1]) / 2
        out.append((string_value, pmi_value))
    return out


def merge(left, right):
    left_items = []
    candidates = []
    right_candidates = []
    for left_item in left:
        found = False
        for right_item in right:
            if is_same(left_item[0], right_item[0]) and not found:
                candidates.append((left_item, right_item))
                right_candidates.append(right_item)
                found = True
        if not found:
            left_items.append(left_item)
    right_items = [i for i in right if i not in right_candidates]
    candidates = merge_candidates(candidates)
    return left_items + candidates + right_items


def merge_lists(list_to_merge):
    if len(list_to_merge) == 1:
        return list_to_merge
    else:
        left, right = split_list(list_to_merge)
    left = merge_lists(left)
    right = merge_lists(right)
    return merge(left, right)


print merge_lists(pmis['Orleans Parish Prison'])
