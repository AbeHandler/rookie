import pdb
import json
import itertools
import collections
import pickle
from pylru import lrudecorator
from rookie.utils import get_document_frequencies, get_pickled
from experiment.simplemerger import Merger
from whoosh.index import open_dir
from collections import defaultdict
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from snippets.prelim import get_snippet
from Levenshtein import distance
import whoosh
from experiment.models import get_metadata_file, get_date_tracker_file

stop_ner = ["The Lens", "THE LENS"]  # TODO refactor this out of the loader

date_tracker = get_date_tracker_file()


def get_caption(name):
    captions_people = pickle.load(open("pickled/people_captions.p", "r"))
    try:
        return captions_people[name]
    except:
        return ""


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

def get_jaccard(one, two):
    one = set(one.split(" "))
    two = set(two.split(" "))
    jacard = float(len(one & two)) / len(one | two)
    return jacard


def get_overview(query, people, organizations, ngrams, top_n=3):
    output = {}
    people = get_counter_and_de_alias('people', people)
    organizations = get_counter_and_de_alias('organizations', organizations)
    ngrams = get_counter_and_de_alias('ngrams', ngrams)

    people_df = get_document_frequencies("people")
    orgs_df = get_document_frequencies("orgs")
    ngrams_df = get_document_frequencies("ngrams")

    ngrams = [(n[0], n[1] * ngrams_df[n[0].upper()]) for n in ngrams]
    ngrams.sort(key=lambda x: x[1])

    people = [(n[0], n[1] * people_df[n[0]]) for n in people]
    people.sort(key=lambda x: x[1])

    organizations = [(n[0], n[1] * orgs_df[n[0]]) for n in organizations]
    organizations.sort(key=lambda x: x[1])

    ngrams = [n for n in ngrams if n[0].upper() != query.upper()]
    people = [n for n in people if n[0].upper() != query.upper()]
    organizations = [n for n in organizations if n[0].upper() != query.upper()]

    ngrams = [n for n in ngrams if n[0] not in stop_ner]
    people = [n for n in people if n[0] not in stop_ner]
    organizations = [n for n in organizations if n[0] not in stop_ner]

    output['terms'] = ((o[0], o[1]) for o in ngrams[-top_n:])
    output['organizations'] = ((o[0], o[1]) for o in organizations[-top_n:])

    people = people[-top_n:]
    people = [(p[0], p[1], get_caption(p[0])) for p in people]
    output['people'] = ((p[0], p[1], p[2]) for p in people)

    return output


def get_counter_and_de_alias(field, subset):
    '''
    Subset is the list of things to be dealiased
    '''
    most_common = collections.Counter(subset).most_common(100)
    aliases = Merger.merge_lists([[o[0]] for o in most_common])
    date_mentions = {}
    for names in aliases:
        master_name = get_representitive_item(names, field)
        if field == 'organizations':
            term_type = 'org'  # TODO: standarize
        if master_name:  # can't always find a master name
            date_mentions = [date_tracker[field][n] for n in names if n in date_tracker[field]]
            total = sum(i[1] for i in most_common if i[0] in names)
            date_mentions = itertools.chain(*date_mentions)
            date_mentions = [i for i in date_mentions]
            replacement = (master_name, total, date_mentions)
            print len(date_mentions)
            print total
            if len(date_mentions) != total:
                # TODO why is this happening?
                pass
            for name in names:
                pop_this = [i for i in most_common if i[0] == name].pop()
                most_common.remove(pop_this)
            most_common.append(replacement)
    return most_common


def standard_path(record):
    return record.get("path").replace("/", "")


def get_metadata(term, results):
    metadata = get_metadata_file()
    tmp = [[i for i in metadata[standard_path(record)][term]] for record in results]
    return list(itertools.chain.from_iterable(tmp))


def get_sentences(results_a):
    metadata = get_metadata_file()
    paths = [standard_path(i) for i in results_a]
    sentences = [[(s, metadata[p]['pubdate'], p) for s in metadata[p]['sentences']] for p in paths]
    return [i for i in itertools.chain.from_iterable(sentences)]


# @lrudecorator(100)
def query_whoosh(qry_string):
    ix = open_dir('rookieindex')
    # qp = MultifieldParser(["title", "people"], schema=ix.schema)
    qp = QueryParser("content", schema=ix.schema)
    q = qp.parse(qry_string)
    results = []
    with ix.searcher() as srch:
        results_a = srch.search(q, limit=None)
        for a in results_a:
            results.append(a.get("path").replace("/", ""))
        all_people = get_metadata("people", results_a)
        all_org = get_metadata("org", results_a)
        all_ngrams = get_metadata("ngram", results_a)
        overview = get_overview(qry_string, all_people, all_org, all_ngrams)
        sentences = get_sentences(results_a)
    return results, overview, sentences


def query_subset(results, term, term_type):
    if term_type == 'organizations':
        term_type = 'org' # TODO: not sure where htis gets mixed up. fix in loader
    if term_type == 'terms':
        term_type = 'ngram'
    metadata = get_metadata_file()
    return [(i, metadata[i]) for i in results if term[0] in metadata[i][term_type]]
