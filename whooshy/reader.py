import pdb
import json
import itertools
from pylru import lrudecorator
from whoosh.index import open_dir
from experiment.cloud_searcher import get_overview
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from snippets.prelim import get_snippet
import whoosh

with open("data/meta_data.json") as inf:
    metadata = json.load(inf)

def get_counter_and_de_alias(field, subset):
    '''
    Subset is the list of things to be dealiased
    '''
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

def standard_path(record):
    return record.get("path").replace("/", "")

def get_metadata(term, results):
    tmp = [[i for i in metadata[standard_path(record)][term]] for record in results]
    return list(itertools.chain.from_iterable(tmp))

def get_sentences(results_a):
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
        term_type = 'org' # not sure where htis gets mixed up. fix in loader
    if term_type == 'terms':
        term_type = 'ngram'
    return [(i, metadata[i]) for i in results if term[0] in metadata[i][term_type]]
    