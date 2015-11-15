import pdb
import json
import itertools
from rookie.rookie import Rookie
from pylru import lrudecorator
from dateutil.parser import parse


@lrudecorator(100)
def get_metadata_file():
    with open("data/meta_data.json") as inf:
        metadata = json.load(inf)
    return metadata


@lrudecorator(100)
def get_date_tracker_file():
    with open("data/date_instances.json") as inf:
        metadata = json.load(inf)
    return metadata



class Parameters(object):

    def __init__(self):
        self.q = None
        self.term = None
        self.termtype = None
        self.current_page = None
        self.startdate = None
        self.enddate = None
        self.docid = None
        self.page = None


def ovelaps_with_query(facet, query_tokens):
    if len(set(facet.split(" ")).intersection(query_tokens)) == 0:
        return False
    else:
        return True


def overlaps_with_output(facet, output):
    '''
    Is this facet already in the list?
    '''
    for i in output:
        if len(set(facet.split(" ")).intersection(i.split(" "))) > 0:
            return True
    return False


def passes_one_word_heuristic(on_deck):
    '''
    Short check for meaningless 1-grams like "commission"
    '''
    if len(on_deck.split(" ")) < 2 and sum(1 for l in on_deck if l.isupper()) < 2:
        return False
    return True


def get_facets(params, n_facets=9):

    '''
    Note this method has to kinds of counters.
    counter % 3 loops over facet types in cycle.
    facet_counters progresses lineararly down each facet list
    '''

    rookie = Rookie("rookieindex")

    results = rookie.query(params.q)

    all_facets = {}

    facet_types = ["people", "org", "ngram"]
     
    # there are 3 facets so counter mod 3 switches
    counter = 0

    stop_facets = set(["THE LENS", "LENS"])

    query_tokens = set(params.q.split(" "))

    facet_counters = {} # a pointer to which facet to include

    for f_type in facet_types:
        all_facets[counter] = rookie.facets(results, f_type)
        facet_counters[counter] = 0
        counter += 1

    output = []

    while len(output) < n_facets:
        try:
            on_deck = all_facets[counter % 3][facet_counters[counter % 3]][0]
            if not ovelaps_with_query(on_deck, query_tokens) and not overlaps_with_output(on_deck, output) and passes_one_word_heuristic(on_deck):
                output.append(all_facets[counter % 3][facet_counters[counter % 3]][0])
        except IndexError: # facet counter is too high? just end loop early
            break
        counter += 1
        facet_counters[counter % 3] += 1

    return output



class Models(object):

    '''Handles logic for the experiment app'''

    @staticmethod
    def get_tokens(docid):
        with open('articles/' + docid) as data_file:    
            data = json.load(data_file)
        return data

    @staticmethod
    def get_headline(docid):
        dt = get_metadata_file()
        return dt[docid]['headline']

    @staticmethod
    def get_pub_date(docid):
        dt = get_metadata_file()
        return dt[docid]['pubdate']

    @staticmethod
    def get_parameters(request):
        '''get parameters'''
        output = Parameters()

        output.q = request.args.get('q')

        output.term = request.args.get('term')

        output.termtype = request.args.get('termtype')

        output.current_page = request.args.get('page')

        try:
            output.current_page = int(output.current_page)
        except:
            output.current_page = 1

        try:
            output.startdate = parse(request.args.get('startdate'))
            if len(output.startdate) == 0:
                output.startdate = None
        except:
            output.startdate = None
        try:
            output.enddate = parse(request.args.get('enddate'))
            if len(output.enddate) == 0:
                output.enddate = None
        except:
            output.enddate = None

        try:
            output.docid = request.args.get('docid')
        except:
            output.docid = None

        output.page = 1

        return output
