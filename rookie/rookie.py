'''
The Rookie engine
'''
import json
import pickle
import itertools
import collections
import pdb
import math
import os
import time
from pylru import lrudecorator
from utils import get_jaccard
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from collections import defaultdict
from Levenshtein import distance

jac_threshold = .6

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


@lrudecorator(100)
def get_metadata_file():
    with open("rookieindex/meta_data.json") as inf:
        metadata = json.load(inf)
    return metadata


class Rookie:
    """The Rookie engine"""
    def __init__(self, path):
        self.path = path
        # for now, just checks if metadata_json is there, if not, runs index
        if "meta_data.json" not in os.listdir(path):
            self.index()
        with open(path + "/meta_data.json") as inf:
            self.metadata = json.load(inf)
        self.people_df = pickle.load(open(self.path + "/people_df.p", "rb"))
        self.orgs_df = pickle.load(open(self.path + "/org_df.p", "rb"))
        self.ngrams_df = pickle.load(open(self.path + "/ngram_df.p", "rb"))

    @staticmethod
    def get_representitive_item(aliases, kind_of_item=None):
        if len(aliases) == 1:
            return aliases[0]
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
                    return scores[1][0]
                if scores[1][0][-1:].upper() == "S":
                    return scores[0][0]
            if len(scores) == 1:
                return scores[0][0]
        elif kind_of_item == "ngrams":
            scores.sort(key=lambda x: x[1])
            max_len = max(len(o[0].split(" ")) for o in scores)
            scores = [o for o in scores if len(o[0].split(" ")) == max_len]
            if len(scores) == 1:
                return scores[0][0]

        # Rookie can't pick anything super smart so just dump out the highest jacaard score
        scores.sort(key=lambda x:x[1], reverse=True)
        return scores[0][0]


    def query(self, qry_string):
        start_time = time.time()
        index = open_dir(self.path)
        query_parser = QueryParser("content", schema=index.schema)
        query = query_parser.parse(qry_string)
        with index.searcher() as srch:
            results_a = srch.search(query, limit=None)
            out = [a.get("path").replace("/", "") for a in results_a]
        #print "[*] querying took {}".format(start_time - time.time())
        return out

    def tfidf(self, word, tf, field):
        if field == "ngram":
            return self.ngrams_df[word.upper()] * tf
        elif field == "org":
            return self.orgs_df[word] * tf
        elif field == "people":
            return self.people_df[word] * tf
        else:
            print "I dont recognize that facet"


    def facets(self, results, field):
        '''
        Get facets for a given field from results set
        Rookie also returns aliases for more downstream processing   
        '''
        tmp = [[i for i in self.metadata[record][field]] for record in results]
        tmp2 = list(itertools.chain.from_iterable(tmp))
        tmp3 = collections.Counter(tmp2).most_common(100)
        aliases = self.de_alias(field, [i[0] for i in tmp3])
        counts = dict(tmp3)
        scores = {}
        # get counts for master name and its aliases
        for master_name in aliases:
            scores[master_name] = counts[master_name]
            for alias in aliases[master_name]:
                scores[master_name] = scores[master_name] + counts[alias]

        # convert each count to a tf idf score
        for score in scores:
            scores[score] = self.tfidf(score, scores[score], field)
        
        scores = [(k,v) for k, v in scores.items()]
        scores.sort(key=lambda x:x[1], reverse=True)

                # for alias in aliases[score[0]]:
                #     if score[0].upper() in mt[r][field].upper():
                #        counter ++

        return scores, aliases


    def de_alias(self, field, subset):
        '''
        Subset is the list of things to be dealiased
        '''
        most_common = collections.Counter(subset).most_common(100)
        aliases = Merger.merge_lists([[o[0]] for o in most_common])
        alias_record = {}
        for names in aliases:
            master_name = Rookie.get_representitive_item(names, field)
            alias_record[master_name] = [i for i in names if i != master_name]
        return alias_record
