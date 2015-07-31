import boto.cloudsearch
import itertools
import heapq
import pdb
from collections import Counter
from rookie.experiment.simplemerger import Merger
from boto.cloudsearch.domain import Domain
import os


def get_search_service():
    conn = boto.connect_cloudsearch2(region="us-west-2",
                    aws_access_key_id=os.environ.get('aws_access_key_id'),
                    aws_secret_access_key=os.environ.get('aws_secret_access_key'))

    domain = conn.lookup('rookie')
    return domain.get_search_service()


def query_cloud_search(query):
    search_service = get_search_service()
    results = search_service.search(q=query)
    pdb.set_trace()
    return results


def get_most_important(results, field, term):
    people = [r['fields'][field] for r in results]
    people = list(itertools.chain.from_iterable(people))
    people = Counter(people)
    people = [(k, v) for k, v in people.items()]
    people = Merger().merge_lists(people)  # TODO why 2x?
    merge = Merger().merge_lists(people)
    return [i for i in merge if i[0].upper() != term.upper()]


def get_top_stuff(results, n, query):
    output = {}
    output['people'] = heapq.nlargest(n, get_most_important(results, 'people', query), key=lambda x: x[1])
    output['organizations'] = heapq.nlargest(n, get_most_important(results, 'organizations', query), key=lambda x: x[1])
    rr = get_most_important(results, 'ngrams', query)
    rr.sort(key=lambda x: x[1])
    output['terms'] = rr[-n:]
    return output