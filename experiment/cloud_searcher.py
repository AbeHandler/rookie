import boto.cloudsearch
import itertools
import heapq
import pdb
from rookie.utils import get_document_frequencies
import collections
import os
from collections import Counter
from experiment.simplemerger import Merger
from pylru import lrudecorator
from Levenshtein import distance
from collections import defaultdict
from rookie import log


stop_ner = ["The Lens", "THE LENS"]  # TODO refactor this out of the loader


def get_search_service():
    conn = boto.connect_cloudsearch2(region="us-west-2",
                    aws_access_key_id=os.environ.get('aws_access_key_id'),
                    aws_secret_access_key=os.environ.get('aws_secret_access_key'))

    domain = conn.lookup('rookie')
    return domain.get_search_service()


@lrudecorator(1000)
def query_cloud_search(query, n=None):
    search_service = get_search_service()
    log.debug("querying cloud search q={}, n={}".format(query, n))
    results = search_service.search(q=query, size=5000)
    log.debug("got restuls")
    return results


def get_counter_and_de_alias(field, results):
    subset = [r['fields'][field] for r in results if field in r['fields'].keys()]
    subset = list(itertools.chain.from_iterable(subset))
    most_common = collections.Counter(subset).most_common(100)
    aliases = Merger.merge_lists([[o[0]] for o in most_common])
    for names in aliases:
        master_name = get_representitive_item(names, field)
        if master_name:  # can't always find a master name
            total = sum(i[1] for i in most_common if i[0] in names)
            replacement = (master_name, total)
            for name in names:
                pop_this = [i for i in most_common if i[0] == name].pop()
                most_common.remove(pop_this)
            most_common.append(replacement)
    return most_common


def get_overview(results, query_term):
    output = {}
    pdb.set_trace()
    people = get_counter_and_de_alias('people', results)
    organizations = get_counter_and_de_alias('organizations', results)
    ngrams = get_counter_and_de_alias('ngrams', results)

    people_df = get_document_frequencies("people")
    orgs_df = get_document_frequencies("orgs")
    ngrams_df = get_document_frequencies("ngrams")

    ngrams = [(n[0], n[1] * ngrams_df[n[0]]) for n in ngrams]
    ngrams.sort(key=lambda x: x[1])

    people = [(n[0], n[1] * people_df[n[0]]) for n in people]
    people.sort(key=lambda x: x[1])

    organizations = [(n[0], n[1] * orgs_df[n[0]]) for n in organizations]
    organizations.sort(key=lambda x: x[1])

    ngrams = [n for n in ngrams if n[0].upper() != query_term.upper()]
    people = [n for n in people if n[0].upper() != query_term.upper()]
    organizations = [n for n in organizations if n[0].upper() != query_term.upper()]

    ngrams = [n for n in ngrams if n[0] not in stop_ner]
    people = [n for n in people if n[0] not in stop_ner]
    organizations = [n for n in organizations if n[0] not in stop_ner]

    output['terms'] = ngrams[-3:]
    output['organizations'] = organizations[-3:]
    output['people'] = people[-3:]

    return output


def get_jaccard(one, two):
    one = set(one.split(" "))
    two = set(two.split(" "))
    jacard = float(len(one & two)) / len(one | two)
    return jacard


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
