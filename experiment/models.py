'''
Application logic for webapp should be in here
'''
import sys
import datetime
import time
import json
import pandas as pd
import itertools
import ujson
import ipdb
import cPickle as pickle
from dateutil.parser import parse
from pylru import lrudecorator
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from rookie.rookie import Rookie
from experiment import log
from experiment.snippet_maker import get_snippet_pg, get_snippet2
from experiment.classes import CONNECTION_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOKIE = Rookie("rookieindex")

engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()

@lrudecorator(100)
def get_pubdate_index():
    t0=time.time()

    try:
        output = pickle.load(open( "PI.p", "rb" ))
        print '[*] found a pickled PI. Using that'
    except:
        print "[*] can't find pickled PI. Builing index from scratch"
        start_time = time.time()
        with open("rookieindex/string_to_pubdate.json") as inf:
            metadata = ujson.load(inf)
        print "[*] loading json took {}".format(time.time() - start_time)
        output = {}
        for key in metadata:
            output[key] = set([parse(p) for p in metadata[key]])
        print "[*] building index took {}".format(time.time() - start_time)
        pickle.dump(output, open("PI.p", "wb" ))
    
    print "pubdate index load took", time.time()-t0
    return output

def get_pubdates_for_ngram(ngram_str):
    """used to be PI[ngram_str]"""
    res = session.connection().execute(
            u"SELECT pubdates FROM ngram_pubdates WHERE ngram=%s",
            ngram_str)
    row = res.fetchone()
    dates = row[0]
    return set(datetime.datetime.strptime(date, "%Y-%m-%d") for date in dates)

@lrudecorator(100)
def get_metadata_file():
    print "Loading metadata file"
    t0=time.time()
    with open("rookieindex/meta_data.json") as inf:
        metadata = ujson.load(inf)
    print "Loaded metadata file in secs:", time.time()-t0
    return metadata

def get_doc_metadata(docid):
    row = session.connection().execute("select data from doc_metadata where docid=%s", docid).fetchone()
    return row[0]

def get_keys(start, stop, bin):
    '''
    Returns a set of date keys between a start and stop date. bin = size of step
    '''
    output = []
    counter = start
    assert bin in ["year", "month", "day"]
    if bin == "month": # TODO
        delta = relativedelta(months=+1)
    elif bin == "year":
        delta = relativedelta(years=+1)
    elif bin == "day":
        delta = relativedelta(days=+1)
    while counter <= stop:
        if bin == "month":
            output.append(str(counter.year) + "-" + str(counter.month))
            counter = counter + delta
    return output

# http://stackoverflow.com/questions/26496831/how-to-convert-defaultdict-of-defaultdicts-of-defaultdicts-to-dict-of-dicts-o
def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.iteritems()}
    return d


def results_to_json_hierarchy(results):
    '''
    Returns a json object with results hierarchically binned by year, month, day
    '''
    start_time = time.time()
    binner = defaultdict(lambda : defaultdict(lambda : defaultdict(list)))
    for r in results:
        pubdate = parse(r["pubdate"])
        binner[pubdate.year][pubdate.month][pubdate.day].append([r["search_engine_index"], str(r["headline"].encode('ascii','ignore')), str(r["pubdate"].encode('ascii','ignore')), str(r["url"].encode('ascii','ignore')), str(r["snippet"].encode('ascii','ignore'))])
    output = default_to_regular(binner)
    print "[*] binning results to json took {}".format(start_time - time.time())
    return output
 

class Parameters(object):

    def __init__(self):
        '''
        An object that holds params from request
        '''
        self.q = None
        self.term = None
        self.termtype = None
        self.startdate = None
        self.enddate = None
        self.docid = None
        self.page = None
        self.zoom = None


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


def make_dataframe(p, facets, results, q_pubdates, aliases):
    '''
    Checks if given username and password match correct credentials.
    :param p: params
    :type username: Parameters
    :param facets: facets
    :type: unicode
    :returns: pandas df. Columns get 1 if facet appears in pubdate
    '''
    df = pd.DataFrame()
    df['id'] = results
    df['pd'] = q_pubdates
    df[p.q] = [1 for i in q_pubdates]
    for facet in facets:
        alias = [get_pubdates_for_ngram(a) for a in aliases[facet]]
        facet_dates = set([i for i in set([i for i in itertools.chain(*alias)]).union(get_pubdates_for_ngram(facet))])
        gus = [int(p) for p in [p in facet_dates for p in q_pubdates]]
        df[facet] = gus
    return df


def passes_one_word_heuristic(on_deck):
    '''
    Short check for meaningless 1-grams like "commission"
    '''
    if len(on_deck.split(" ")) < 2 and sum(1 for l in on_deck if l.isupper()) < 2:
        return False
    return True


class Models(object):

    @staticmethod
    def get_headline(docid):
        return get_doc_metadata(docid)['headline']

    @staticmethod
    def get_pub_date(docid):
        return get_doc_metadata(docid)['pubdate']

    @staticmethod
    def get_message(l_results, params, len_doc_list, PAGE_LENGTH):
        if params.page < 1:
            params.page == 1
        start = ((params.page - 1) * PAGE_LENGTH) + 1
        end = start + PAGE_LENGTH + 1
        output = "{} total results for {}.".format(l_results, params.q)
        return output

    @staticmethod
    def get_parameters(request):
        '''get parameters'''
        output = Parameters()

        output.q = request.args.get('q').replace("_", " ")

        output.term = request.args.get('term')

        output.termtype = request.args.get('termtype')

        output.page = request.args.get('page')

        try:
            output.page = int(output.page)
        except:
            output.page = 1

        try:
            output.startdate = parse(request.args.get('startdate'))
        except:
            print "could not parse start date {}".format(request.args.get('startdate'))
            output.startdate = None
        try:
            output.enddate = parse(request.args.get('enddate'))
        except:
            output.enddate = None

        try:
            output.docid = request.args.get('docid')
        except:
            output.docid = None

        # TODO: remove. replaced w/ F
        try:
            output.detail = request.args.get('detail').replace("_", " ")
        except:
            output.detail = None

        try:
            output.f = request.args.get('f')
        except:
            output.f = None
    
        try:
            output.date_detail = request.args.get('date_detail')
        except:
            output.date_detail = None

        try:
            output.zoom = request.args.get('zoom')
            print "got zoom {}".format(output.zoom)
        except:
            output.zoom = "year" # default zoom to a year

        return output

    @staticmethod
    def get_results(params):

        '''
        Just query whoosh
        '''

        results = ROOKIE.query(params.q)
        return results

    @staticmethod
    def date_filter(results, params):
        '''
        Filter results by date
        '''
        if params.startdate is not None and params.enddate is not None:
            md = lambda r: get_doc_metadata(r)
            return [r for r in results if parse(md(r)["pubdate"]) > params.startdate and parse(md(r)["pubdate"]) < params.enddate]
        else:
            return results

    @staticmethod
    def f_occurs_filter(results, facet, aliases):
        '''
        filter results for when f or one of its aliases occurs
        '''
        # BTO: it appears that aliases never includes the original facet label.
        # AH: yeah that is correct. in the alias grouping code the facet label is the key and the aliases are value
        alias_set = set([facet] + list(aliases))
        good_docs = []
        for r in results:
            ngrams = get_doc_metadata(r)['ngram']
            # AH --> added these two below. otherwise the timeseries graph is not correct
            ngrams = ngrams + get_doc_metadata(r)['people']
            ngrams = ngrams + get_doc_metadata(r)['org']
            ngrams = set(ngrams)
            if alias_set & ngrams:
                good_docs.append(r)
        return good_docs

    @staticmethod
    def get_doclist(results, params, PAGE_LENGTH, aliases=None):
        doc_results = []
        if params.page < 1:
            params.page == 1
        # chop off to only relevant results
        start = ((params.page - 1) * PAGE_LENGTH)
        end = start + PAGE_LENGTH
        # results = results[start:end]

        # AH: assuming the order of results is not changed since coming out from IR system
        for whoosh_index, r in enumerate(results):
            d = get_doc_metadata(r)
            pubdate = parse(d['pubdate'])
            doc_results.append({
                'search_engine_index': whoosh_index,
                'pubdate': d['pubdate'].encode("ascii", "ignore"),
                'headline': d['headline'].encode("ascii", "ignore"),
                'url': d['url'].encode("ascii", "ignore"),
                'year': pubdate.year,
                'month': pubdate.month,
                'day': pubdate.day,
                'snippet': Models.get_snippet(r, params.q, f=params.detail, aliases=aliases).encode("ascii", "ignore")
            })
        return doc_results


    @staticmethod
    def get_status(params):
        return ""


    @staticmethod
    def get_snippet(docid, q, f=None, aliases=None, nchar=200):

        f_aliases = set() if aliases is None else set(aliases)
        if f is not None:
            f_aliases.add(f)
        hsents = get_snippet2(docid, q, f_aliases, 
                taginfo=dict(
                    q_ltag='<span style="font-weight:bold;color:black">',
                    q_rtag='</span>',
                    f_ltag='<span style="font-weight:bold;color:#b33125">',
                    f_rtag='</span>',)
                )

        if len(hsents)==0:
            return ""

        if len(hsents)==1:
            return hsents[0]['htext']

        assert len(hsents) <= 2
        dist = hsents[1]['sentnum'] - hsents[0]['sentnum']
        sep = " " if dist == 1 else " ... "
        return hsents[0]['htext'] + sep + hsents[1]['htext']

    @staticmethod
    def get_facets(params, results, n_facets=9):

        '''
        Note this method has to kinds of counters.
        counter % 3 loops over facet types in cycle.
        facet_counters progresses lineararly down each facet list
        '''

        all_facets = {}

        facet_types = ["people", "org", "ngram"]
         
        # there are 3 facets so counter mod 3 switches
        counter = 0

        stop_facets = set(["THE LENS", "LENS"])

        query_tokens = set(params.q.split(" "))

        facet_counters = {} # a pointer to which facet to include
        
        all_aliases = {}

        # Get each of the facets
        for f_type in facet_types:
            tmpfacets, newaliases = ROOKIE.facets(results, f_type)
            all_facets[counter] = tmpfacets
            all_aliases.update(newaliases)
            facet_counters[counter] = 0
            counter += 1

        output = []

        log.debug('got facets. time to filter')
        # Figure out which facets to include in the UI
        while len(output) < n_facets:
            try:
                on_deck = all_facets[counter % 3][facet_counters[counter % 3]][0]
                if not ovelaps_with_query(on_deck, query_tokens) and not overlaps_with_output(on_deck, output) and passes_one_word_heuristic(on_deck):
                    output.append(all_facets[counter % 3][facet_counters[counter % 3]][0])
            except IndexError: # facet counter is too high? just end loop early
                break
            counter += 1
            facet_counters[counter % 3] += 1
        return output, all_aliases
