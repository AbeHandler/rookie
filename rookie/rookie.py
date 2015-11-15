'''
The Rookie engine
'''
import json
import pickle
import itertools
import collections
import pdb
from utils import get_jaccard
from experiment.simplemerger import Merger
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from collections import defaultdict
from Levenshtein import distance


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


class Rookie:
    """The Rookie engine"""
    def __init__(self, path):
        self.path = path
        with open(path + "/meta_data.json") as inf:
            self.metadata = json.load(inf)
        self.people_df = pickle.load(open(self.path + "/df_people.p", "rb"))
        self.orgs_df = pickle.load(open(self.path + "/df_orgs.p", "rb"))
        self.ngrams_df = pickle.load(open(self.path + "/df_ngrams.p", "rb"))


    def index(self, documents):
        # load into whoosh and index what you need
        return 'hello world'


    def query(self, qry_string):
        index = open_dir(self.path)
        query_parser = QueryParser("content", schema=index.schema)
        query = query_parser.parse(qry_string)
        with index.searcher() as srch:
            results_a = srch.search(query, limit=None)
            return [a.get("path").replace("/", "") for a in results_a]


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
        '''get facets from results set'''
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
        return scores


    def de_alias(self, field, subset):
        '''
        Subset is the list of things to be dealiased
        '''
        most_common = collections.Counter(subset).most_common(100)
        aliases = Merger.merge_lists([[o[0]] for o in most_common])
        alias_record = {}
        for names in aliases:
            master_name = get_representitive_item(names, field)
            alias_record[master_name] = [i for i in names if i != master_name]
        return alias_record
