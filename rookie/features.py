import json
import re
import pdb
from Levenshtein import distance
from rookie.utils import stop_word, get_picked
from rookie import LAMBDA


class Featureizer(object):
    """
    Get features to decide if two terms are the same
    """

    @staticmethod
    def get_json(key_name):
        try:
            with open("data/pmis/" + key_name + ".json", "r") as infile:
                one = json.load(infile)
                return set([i[0] for i in one if not stop_word(i[0])])
        except IOError:
            return set()
        except ValueError:
            return set()

    @staticmethod
    def get_count(term):
        try:
            return float(get_picked("counts.p")[term])
        except KeyError:
            return float(get_picked("unigrams.p")[term])

    @staticmethod
    def get_features(term1, term2):
        features = {}
        features['levenshtein'] = Featureizer.get_levenshtein(term1, term2)
        features['lidstone'] = Featureizer.get_lidstone(term1, term2)
        features['jaccard'] = Featureizer.get_jaccard(term1, term2)
        features['pmi_overlap'] = Featureizer.get_pmi_overlap(term1, term2)
        return features

    @staticmethod
    def get_levenshtein(term1, term2):
        '''
        Levenshtein distance
        '''
        return distance(term1, term2)

    @staticmethod
    def get_lidstone(term1, term2):
        '''
        Probability of longer term (counting by tokens) given shorter term
        '''
        # if there is no intersection, return 0
        if len(set(term1.split(" ")).intersection(set(term2.split(" ")))) == 0:
            return 0

        if not((term1 in term2) or (term2 in term1)):
            return 0

        # if the terms are the same size, return 0s
        if len(term1.split(" ")) == len(term2.split(" ")):
            return 0
        else:
            bigger = max([term1, term2],
                         key=lambda x: len(x.split(" ")))
            smaller = min([term1, term2],
                          key=lambda x: len(x.split(" ")))
            given = re.findall(smaller, bigger)[0]
            potential = bigger.replace(given, "").strip()
            potential = re.sub(' +', ' ', potential)
            COUNT_VOCAB = len(get_picked("unigrams.p").keys())
            num = Featureizer.get_count(potential) + LAMBDA
            denom = Featureizer.get_count(given) + (COUNT_VOCAB * LAMBDA)
            return num / denom

    @staticmethod
    def get_jaccard(term1, term2):
        term1 = set(term1.split(" "))
        term2 = set(term2.split(" "))
        jacard = float(len(term1 & term2)) / len(term1 | term2)
        return jacard

    @staticmethod
    def get_pmi_overlap(term1, term2):
        '''
        Each term has a window of associated high PMI terms.
        Ex: 'consent decree' is associated with Orleans Parish Prison
        This method comuptes the jaccard overlap between PMI windows.
        '''
        set_1 = Featureizer.get_json(term1)
        set_2 = Featureizer.get_json(term2)
        n = len(set_1.intersection(set_2))
        try:
            return n / float(len(set_1) + len(set_2) - n)
        except ZeroDivisionError:
            return 0
