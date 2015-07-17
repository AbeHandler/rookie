import itertools
import pdb


class KeyMerge(object):

    def __init__(self, keys):
        self.keys = keys

    def compute_jaccard_index(self, set_1, set_2):
        n = len(set_1.intersection(set_2))
        return n / float(len(set_1) + len(set_2) - n)

    def get_keys_to_merge(self):
        joiners = []

        for i in itertools.product(self.keys, self.keys):
            jac = self.compute_jaccard_index(set(i[0].split(" ")), set(i[1].split(" ")))
            if jac > .5 and jac < 1 and len(i[0]) > 2 and len(i[1]) > 2:
                joiners.append((i[0], i[1], jac))

        joiners = set(joiners)

        return joiners

# keys = [o.replace("\n", "").split(" ") for o in open("pmistmp", "r")]
# merger = KeyMerge(keys
# merger = KeyMerge([["President", "Barack", "Houssein", "Obama"], ["Senator", "Barack",  "Houssein", "Obama"]])
# print merger.get_keys_to_merge()
