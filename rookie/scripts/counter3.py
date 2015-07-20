'''
Find aliases in the keys
'''
import pdb
import json
import pickle
from rookie import log
from rookie import files_location
from collections import defaultdict
from rookie import jac_threshold
from rookie.pmismerger import KeyMerge

keys = [o.replace("\n", "") for o in open("keys.csv", "r")]
instances = pickle.load(open("instances.p", "rb"))

# TODO some of the keys are not associated with PMIS


# TODO get to the biggest alias
# $ cat keys.csv | grep 'Sen. J.P.'
# state Sen. J.P.
# Sen. J.P.
# Sen. J.P. Morrell

aliases = defaultdict(list)


def compute_jaccard_index(set_1, set_2):
    n = len(set_1.intersection(set_2))
    return n / float(len(set_1) + len(set_2) - n)


def merge_the_candicates(candidates):
    log.info(len(candidates))
    for key in candidates:
        try:
            with open("data/pmis/" + key[0] + ".json", "r") as infile:
                one = json.load(infile)
                set_one = set(" ".join([i[0] for i in one]).split(" "))
            with open("data/pmis/" + key[1] + ".json", "r") as infile:
                two = json.load(infile)
                set_two = set(" ".join([i[0] for i in two]).split(" "))
            jac = compute_jaccard_index(set_one, set_two)
            if jac >= jac_threshold:
                big = max([key[0], key[1]], key=lambda x: len(x))
                small = min([key[0], key[1]], key=lambda x: len(x))
                # add small to aliases
                aliases[big].append(small)
                # pick up the small's aliases as well
                aliases[big] = aliases[big] + aliases[small]
                # remove small from aliases
                aliases.pop(small, None)
        except IOError:
            pass

merger = KeyMerge(keys)
keys_to_merge_candidates = merger.get_keys_to_merge()
merge_the_candicates(keys_to_merge_candidates)

counter = 0

more_merge = KeyMerge(aliases.keys()).get_keys_to_merge()
memory_merge = -1

# Run until there are no more that can be merged
# (i.e. memery merge does not change on loop)
while len(more_merge) > 0 and len(more_merge) != memory_merge:
    memory_merge = len(more_merge)
    pdb.set_trace()
    log.info("round " + str(counter))
    counter = counter + 1
    merge_the_candicates(more_merge)
    more_merge = KeyMerge(aliases.keys()).get_keys_to_merge()


pickle.dump(aliases, open(files_location + "aliases.p", "wb"))
