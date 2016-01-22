'''
Application logic for webapp should be in here
'''
import datetime
import time
import pandas as pd
import ujson
import ipdb
import cPickle as pickle
from dateutil.parser import parse
from pylru import lrudecorator
from joblib import Memory
from tempfile import mkdtemp
from dateutil.relativedelta import relativedelta
from rookie.rookie import Rookie
from experiment.snippet_maker import get_snippet2
from experiment.classes import CONNECTION_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


cachedir = mkdtemp()

ROOKIE = Rookie("rookieindex")

memory = Memory(cachedir=cachedir, verbose=0)

engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()



def filter_results_with_binary_dataframe(results, facet, df):
    '''
    take a binary dataframe indicating which facets occur
    '''
    hits = df.loc[df[facet] == 1]["id"].tolist()
    for h in hits:
        assert h in results
    return hits


@memory.cache
def results_to_doclist(results, q, f, aliases):
    '''
    Start w/ search results. filter based on params. get a doclist back.
    '''
    metadata = [get_doc_metadata(r) for r in results]
    q_pubdates = [parse(h["pubdate"]) for h in metadata]
    df = make_dataframe(q, [f], results, q_pubdates, aliases)
    results = filter_results_with_binary_dataframe(results, f, df)
    fdoc_list = Models.get_doclist(results, q, f, aliases=aliases)
    return fdoc_list


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

def get_keys(q_pubdates, bin):
    '''
    Returns a set of date keys between a start and stop date. bin = size of step
    '''
    try:
        start = min(q_pubdates)
        stop = max(q_pubdates)
    except ValueError: # this means pubdates == []
        return [] # being pythonic and leaping before looking
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
 

class Parameters(object):

    def __init__(self):
        '''
        An object that holds params from request
        '''
        self.q = None
        self.f = None
        self.startdate = None
        self.enddate = None
        self.zoom = None

    def __repr__(self):
        return "<Parameters (q={}, detail={}, startdate={}, enddate={}, zoom={})>".format(
            self.q, self.f, self.startdate, self.enddate, self.zoom)


def get_val_from_df(val_key, dt_key, df, binsize="month"):
    '''
    :param val_key: a facet
    :param dt_key: a date string. usually, YYYY-M. formatted 2014-5
    :param df:  a dataframe
    :param binsize: ignored for now. needed for dateparsing in try methods
    :return:
    '''
    try:
        return df[val_key][int(dt_key.split("-")[0])][int(dt_key.split("-")[1])]
    except KeyError:
        return 0


def bin_dataframe(df, binsize):
    '''
    :param df: binary df of what facets show up in what doc_results
    :param binsize: ex. "month" or "year"
    :return: df that counts how many times facets show up in a bin
    '''
    if binsize == "year":
        df = df.groupby([df['pd'].map(lambda x: x.year)]).sum().unstack(0).fillna(0)
    elif binsize == "month":
        df = df.groupby([df['pd'].map(lambda x: x.year), df['pd'].map(lambda x: x.month)]).sum().unstack(0).fillna(0)
    else:
        assert binsize == "day"
        df = df.groupby([df['pd'].map(lambda x: x.year), df['pd'].map(lambda x: x.month), df['pd'].map(lambda x: x.day)]).sum().unstack(0).fillna(0)
    return df


def make_dataframe(q, facets, results, q_pubdates, aliases):
    '''
    :param q: params.q
    :type username: Parameters
    :param facets: facets
    :type: unicode
    :returns: pandas df. Columns get 1 if facet appears in pubdate
    '''
    df = pd.DataFrame()
    df['id'] = results
    df['pd'] = q_pubdates
    df[q] = [1 for i in q_pubdates]
    for facet in facets:
        facet_dates = [i for i in set([i for i in get_pubdates_for_ngram(facet)])]
        #TODO
        #alias = [get_pubdates_for_ngram(a) for a in aliases[facet]]
        # facet_dates = set([i for i in set([i for i in itertools.chain(*alias)]).union(get_pubdates_for_ngram(facet))])
        gus = [int(p) for p in [p in facet_dates for p in q_pubdates]]
        df[facet] = gus
    return df


class Models(object):

    @staticmethod
    def get_parameters(request):
        '''get parameters'''
        output = Parameters()

        output.q = request.args.get('q').replace("_", " ")

        try:
            output.startdate = parse(request.args.get('startdate'))
        except:
            output.startdate = None
        try:
            output.enddate = parse(request.args.get('enddate'))
        except:
            output.enddate = None

        try:
            output.f = request.args.get('f')
        except:
            output.f = None
    
        try:
            output.zoom = request.args.get('zoom')
        except:
            output.zoom = "year" # default zoom to a year

        return output

    @staticmethod
    def get_results(params):

        '''
        Just query whoosh
        '''

        results = ROOKIE.query(params.q)
        return tuple(results)


    @staticmethod
    def get_doclist(results, q, f, aliases=None):
        doc_results = []

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
                'snippet': Models.get_snippet(r, q, f, aliases=aliases).encode("ascii", "ignore")
            })
        return doc_results


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