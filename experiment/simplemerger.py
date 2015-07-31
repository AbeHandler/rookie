import math
import itertools
import pdb
from rookie.experiment import log
from rookie.experiment import jac_threshold
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
    def item_is_same(one, two):
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
        if Merger.get_jaccard(one, two) >= jac_threshold:
            return True
        else:
            return False

    @staticmethod
    def is_same(one, two):
        '''
        Try to see if these two lists are the same
        '''
        items = [i for i in itertools.product(*[one, two]) if i[0] != i[1]]
        total = 0
        are_same = 0
        for item1 in one:
            for item2 in two:
                if Merger.item_is_same(item1, item2):
                    are_same += 1
                total += 1
        if float(are_same)/float(total) > .25:
            return True
        else:
            return False

    @staticmethod
    def merge(left, right):
        output = []
        for i in range(0, len(left)):
            left_item = left[i]
            found = False
            for i in range(0, len(right)):
                right_item = right[i]
                if Merger.is_same(left_item, right_item) and not found:
                    right[i] = right_item + left_item
                    found = True
            if not found:
                output.append(left_item)
        output = output + right
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