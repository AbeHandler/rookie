'''
The Rookie engine
'''
import json
import pickle
import itertools
import collections
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

    def facets(self, results, field):
        '''get facets from results set'''
        tmp = [[i for i in self.metadata[record][field]] for record in results]
        tmp2 = list(itertools.chain.from_iterable(tmp))
        stuff = self.get_counter_and_de_alias(field, tmp2)
        return stuff

    def get_counter_and_de_alias(self, field, subset):
        '''
        Subset is the list of things to be dealiased
        '''
        most_common = collections.Counter(subset).most_common(100)
        aliases = Merger.merge_lists([[o[0]] for o in most_common])
        date_mentions = {}
        for names in aliases:
            master_name = get_representitive_item(names, field)
            if field == 'organizations':
                field = 'org'  # TODO: standarize
            if field == "ngrams":
                field = "ngram"
            if master_name:  # can't always find a master name
                total = sum(i[1] for i in most_common if i[0] in names)
                date_mentions = itertools.chain(*date_mentions)
                date_mentions = [i for i in date_mentions]
                replacement = (master_name, total, date_mentions)
                if len(date_mentions) != total:
                    # TODO why is this happening?
                    pass
                for name in names:
                    pop_this = [i for i in most_common if i[0] == name].pop()
                    most_common.remove(pop_this)
                most_common.append(replacement)
        return most_common



        # metadata = get_metadata_file()
        # tmp = [[i for i in metadata[standard_path(record)][term]] for record in results]
        # return list(itertools.chain.from_iterable(tmp))
