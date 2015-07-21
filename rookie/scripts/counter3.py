'''
Find aliases in the keys
'''
import pdb
import json
import pickle
from rookie import log
from rookie.utils import get_picked
from rookie import files_location
from collections import defaultdict
from rookie import jac_threshold
from rookie.pmismerger import KeyMerge
from rookie.utils import stop_word


def compute_jaccard_index(set_1, set_2):
    n = len(set_1.intersection(set_2))
    return n / float(len(set_1) + len(set_2) - n)


def get_json(key_name):
    with open("data/pmis/" + key_name + ".json", "r") as infile:
        one = json.load(infile)
        set_one = set([i[0] for i in one if not stop_word(i[0])])
        # I was doing bow, but seems better to keep multi grams together
        # set_one = set(" ".join([i[0] for i in one]).split(" "))
        return set_one


def mergeable(one, two):
    set_one = get_json(one)
    set_two = get_json(two)
    jac = compute_jaccard_index(set_one, set_two)
    if jac >= jac_threshold:
        return True
    else:
        return False


def merge_the_candicates(candidates, count):
    log.info(len(candidates))
    for key in candidates:
        try:
            if mergeable(key[0], key[0]):
                big = max([key[0], key[1]], key=lambda x: len(x))
                small = min([key[0], key[1]], key=lambda x: len(x))

                # Orleans police departments should be merged to
                # Orleans Police Department
                # TODO move this logic into merger
                if big[-1:] == "s" and len(big) == len(small) + 1:
                    tmp = big
                    big = small
                    small = tmp
                lg = "merging {} into {}, round {}".format(small, big, count)
                log.info(lg)
                # add small to aliases
                aliases[big].append(small)
                # pick up the small's aliases as well
                aliases[big] = aliases[big] + aliases[small]
                # remove small from aliases
                aliases.pop(small, None)
        except IOError:
            log.error("i/o: cant read file {} {}".format(key[0], key[1]))
        except ValueError:
            log.error("value: cant read file {} {}".format(key[0], key[1]))


if __name__ == "__main__":
    keys = [o.replace("\n", "") for o in open("keys.csv", "r")]
    instances = get_picked("instances.p")

    # TODO some of the keys are not associated with PMIS

    # TODO get to the biggest alias
    # $ cat keys.csv | grep 'Sen. J.P.'
    # state Sen. J.P.
    # Sen. J.P.
    # Sen. J.P. Morrell

    aliases = defaultdict(list)
    merger = KeyMerge(keys)
    keys_to_merge_candidates = merger.get_keys_to_merge()

    counter = 0
    merge_the_candicates(keys_to_merge_candidates, counter)

    more_merge = KeyMerge(aliases.keys()).get_keys_to_merge()
    memory_merge = -1

    # Run until there are no more that can be merged
    # (i.e. memery merge does not change on loop)
    while len(more_merge) > 0 and len(more_merge) != memory_merge:
        memory_merge = len(more_merge)
        log.info("round " + str(counter))
        counter = counter + 1
        merge_the_candicates(more_merge, counter)
        more_merge = KeyMerge(aliases.keys()).get_keys_to_merge()

    pickle.dump(aliases, open(files_location + "aliases.p", "wb"))
