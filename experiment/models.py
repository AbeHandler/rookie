# import ipdb
import sys
import time
import json
import pandas as pd
import itertools
import ujson
import cPickle as pickle
from pylru import lrudecorator
from collections import defaultdict
from dateutil.parser import parse
from rookie.classes import IncomingFile
from rookie.rookie import Rookie
from experiment import log, CORPUS_LOC
from experiment.snippet_maker import get_snippet_pg
from nltk.tokenize import word_tokenize
from experiment.classes import CONNECTION_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOKIE = Rookie("rookieindex")

engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()

@lrudecorator(100)
def get_pubdate_index():

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
    
    return output

PI = get_pubdate_index()

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
        alias = [PI[a] for a in aliases[facet]]
        facet_dates = set([i for i in set([i for i in itertools.chain(*alias)]).union(PI[facet])])
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
    def get_tokens(docid):
        with open('articles/' + docid) as data_file:    
            data = json.load(data_file)
        return data

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
        output = "{} total results for {}. Showing {} thru {}".format(l_results, params.q, start, end)
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

        try:
            output.detail = request.args.get('detail').replace("_", " ")
        except:
            output.detail = None
    
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
    def f_occurs_filter(results, params, aliases):
        '''
        filter results for when f or one of its aliases occurs
        '''
        f_dates = [i for i in PI[params.detail]]
        f_alias_dates = [i for i in itertools.chain(*[PI[a] for a in aliases])]
        q_f_pubdates = [r for r in results if parse(get_doc_metadata(r)["pubdate"]) in f_dates + f_alias_dates]
        return q_f_pubdates


    @staticmethod
    def get_doclist(results, params, PAGE_LENGTH):
        output = []
        if params.page < 1:
            params.page == 1
        # chop off to only relevant results
        start = ((params.page - 1) * PAGE_LENGTH)
        end = start + PAGE_LENGTH
        results = results[start:end]
        for r in results:
            d = get_doc_metadata(r)
            output.append((d['pubdate'], d['headline'], d['url'], Models.get_snippet(r, params.q, params.detail)))
        return output


    @staticmethod
    def get_status(params):
        if params.zoom == "year":
            try:
                status = "Documents containing <span style='font-weight: bold;'>{}</span> and <span style='font-weight:bold;'>{}</span> from {} to {}".format(params.q, params.detail, params.startdate.year, params.enddate.year)
            except AttributeError:
                status = "Documents containing <span style='font-weight: bold; '>{}<span> and <span style='font-weight:bold;'>{}</span>".format(params.q, params.detail)
        if params.zoom == "month":
            try:
                status = "Documents containing <span style='font-weight: bold ; '>{}</span> and <span style='font-weight:bold;'>{}</span> from {}, {}".format(params.q, params.detail, params.startdate.strftime("%B"), params.enddate.strftime("%Y"))
            except AttributeError:
                status = "Documents containing <span style='font-weight: bold ; '>{}</span> and <span style='font-weight:bold;'>{}</span>".format(params.q, params.detail)
        if params.zoom == "None":
            status = "Documents containing <span style='font-weight: bold ; '>{}</span> and <span style='font-weight:bold;'>{}</span>".format(params.q, params.detail)
        return status


    @staticmethod
    def get_snippet(docid, q, f, nchar=200):
        #TODO: add aliasing. remove set sorting
        start_time = time.time()
        snippet = get_snippet_pg(docid, q, f)
        print "[*] building snippet took {}".format(start_time - time.time())

        return snippet[0].text + " ... " + snippet[1].text

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
