import math
import pdb
from rookie.utils import get_pmi
from Levenshtein import distance


class Merger(object):
    """
    A gram type or a NER type
    """

    @staticmethod
    def split_list(input_list):
        half = len(input_list)/2
        return input_list[:half], input_list[half:]

    @staticmethod
    def get_jaccard(one, two):
        one = set(one.split(" "))
        two = set(two.split(" "))
        jacard = float(len(one & two)) / len(one | two)
        return jacard

    @staticmethod
    def is_same(one, two):
        if distance(one, two) < 2:
            return True
        set_dif = math.fabs(len(one.split(" ")) - len(two.split(" ")))
        if set_dif > 0 and set_dif < 3:
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
        if Merger.get_jaccard(one, two) >= .5:
            return True
        else:
            return False

    @staticmethod
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

    @staticmethod
    def merge(left, right):
        left_items = []
        candidates = []
        right_candidates = []
        for left_item in left:
            found = False
            for right_item in right:
                if Merger.is_same(left_item[0], right_item[0]) and not found:
                    candidates.append((left_item, right_item))
                    right_candidates.append(right_item)
                    found = True
            if not found:
                left_items.append(left_item)
        right_items = [i for i in right if i not in right_candidates]
        candidates = Merger.merge_candidates(candidates)
        output = left_items + candidates + right_items
        return output

    @staticmethod
    def merge_lists(list_to_merge):
        if len(list_to_merge) == 1 or len(list_to_merge) == 0:
            return list_to_merge
        else:
            left, right = Merger.split_list(list_to_merge)
        right = Merger.merge_lists(right)
        left = Merger.merge_lists(left)
        return Merger.merge(left, right)
