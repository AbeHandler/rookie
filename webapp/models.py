'''
Application logic for webapp should be in here
'''
import datetime
import ipdb
import ujson
import time
import cPickle as pickle
import pandas as pd
from dateutil.parser import parse
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from dateutil.relativedelta import relativedelta
from webapp.snippet_maker import get_snippet2, get_snippet3
from webapp import CONNECTION_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from facets.query_sparse import get_facets_for_q, load_all_data_structures
from pylru import lrudecorator
import traceback

ENGINE = create_engine(CONNECTION_STRING)
SESS = sessionmaker(bind=ENGINE)
SESSION = SESS()

@lrudecorator(100)
def get_urls_xpress(corpus):
    with open("indexes/{}/urls_xpress.p".format(corpus)) as inf:
        return pickle.load(inf)

@lrudecorator(100)
def get_pubdates_xpress(corpus):
    with open("indexes/{}/pubdates_xpress.p".format(corpus)) as inf:
        return pickle.load(inf)

@lrudecorator(100)
def get_headline_xpress(corpus):
    #ipdb.set_trace()
    with open("indexes/{}/headlines_xpress.p".format(corpus)) as inf:
        return pickle.load(inf)


def get_stuff_ui_needs(params, results):
    try:

        binned_facets = get_facets_for_q(params.q, results, 200, load_all_data_structures(params.corpus))

        aliases = [] # TODO
        stuff_ui_needs = {}
        q_pubdates = [load_all_data_structures(params.corpus)["pubdates"][int(r)] for r in results]

        binsize = "month"

        df = make_dataframe(params.q, binned_facets["g"], results, q_pubdates, aliases)
        df = bin_dataframe(df, binsize)

        keys = get_keys(params.corpus)

        q_data = [get_val_from_df(params.q, key, df, binsize) for key in keys]

        stuff_ui_needs["keys"] = [k + "-01" for k in keys]
        display_bins = []
        for key in binned_facets:
            if key != "g":
                display_bins.append({"key": key, "facets": binned_facets[key]})


        stuff_ui_needs["total_docs_for_q"] = len(results)
        facets = {}
        for fac in binned_facets['g']:
            facets[fac] = [get_val_from_df(fac, key, df, binsize) for key in keys]
        stuff_ui_needs["facet_datas"] = facets

        dminmax = corpus_min_max(params.corpus)

        try:
            stuff_ui_needs["first_story_pubdate"] = dminmax["min"]
            stuff_ui_needs["last_story_pubdate"] = dminmax["max"]
        except ValueError:
            stuff_ui_needs["first_story_pubdate"] = ""
            stuff_ui_needs["last_story_pubdate"] = ""
        stuff_ui_needs["corpus"] = params.corpus
        stuff_ui_needs["query"] = params.q
        stuff_ui_needs["q_data"] = q_data
        stuff_ui_needs["global_facets"] = binned_facets['g']
        return stuff_ui_needs
    except:
        with open('log/error.txt', 'a') as f:
            traceback.print_exc(file=f)

def query(qry_string, corpus):
    '''
    Query whoosh
    '''
    index = open_dir("indexes/{}/".format(corpus))
    query_parser = QueryParser("content", schema=index.schema)
    qry = query_parser.parse(qry_string)
    with index.searcher() as srch:
        results_a = srch.search(qry, limit=None)
        out = [a.get("path").replace("/", "") for a in results_a]
    return out


def filter_results_with_binary_dataframe(results, facet, df):
    '''
    take a binary dataframe indicating which facets occur
    '''
    hits = df.loc[df[facet] == 1]["id"].tolist()
    for h in hits:
        assert h in results
    return hits

def corpus_min_max(corpus):
    """get the min/max pubdates for a corpus"""
    res = SESSION.connection().execute(
            u"SELECT * FROM corpora WHERE corpusname=%s",
            corpus)
    res2 = [r for r in res][0]
    return {"min": res2[2], "max": res2[3]}

def results_to_doclist(results, q, f, corpus, pubdates, aliases):
    '''
    Start w/ search results. filter based on params. get a doclist back.
    '''
    q_pubdates = [pubdates[int(r)] for r in results]
    df = make_dataframe(q, [f], results, q_pubdates, aliases)
    results = filter_results_with_binary_dataframe(results, f, df)
    fdoc_list = Models.get_doclist(results, q, f, corpus, aliases=aliases)
    filtered_pubdates = [pubdates[int(r)] for r in results]
    return filtered_pubdates, fdoc_list


def get_pubdates_for_ngram(ngram_str):
    """used to be PI[ngram_str]"""
    res = SESSION.connection().execute(
            u"SELECT pubdates FROM ngram_pubdates WHERE ngram=%s",
            ngram_str)
    row = res.fetchone()
    dates = row[0]
    return set(datetime.datetime.strptime(date, "%Y-%m-%d") for date in dates)


def getcorpusid(corpus):
    '''
    Get corpus id for corpus name
    '''
    go = lambda *args: SESSION.connection().execute(*args)
    cid = go("select corpusid from corpora where corpusname='{}'".format(corpus)).fetchone()[0]
    return cid
        

@lrudecorator(3000)
def get_doc_metadata(docid, corpus):
    '''
    Just query db for function metatdata
    '''

    corpusid = getcorpusid(corpus)
    row = SESSION.connection().execute("select data from doc_metadata where docid=%s and corpusid=%s", docid, corpusid).fetchone()
    return row[0]

def filter_f(results, params):
    if params.f is None:
        return results
    ds = load_all_data_structures(params.corpus)["vectors"]
    f_ngram_no = load_all_data_structures(params.corpus)["decoders"]["ngram"][params.f]
    rev_decoders = load_all_data_structures(params.corpus)["reverse_decoders"]
    return [r for r in results if unicode(f_ngram_no) in ds[r]]


def get_keys(corpus):
    '''
    Returns a set of date keys between a start and stop date. bin = size of step
    '''
    min_max = corpus_min_max(corpus)
    start = min_max["min"]
    stop =  min_max["max"]
    output = []
    counter = start

    while counter <= stop:
        output.append(counter.strftime("%Y-%m"))
        counter = counter + relativedelta(months=+1)
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
        self.corpus = None

    def __repr__(self):
        return "<Parameters (q={}, detail={}, startdate={}, enddate={})>".format(
            self.q, self.f, self.startdate, self.enddate)


def get_val_from_df(val_key, dt_key, df, binsize="month"):
    '''
    :param val_key: a facet
    :param dt_key: a date string. usually, YYYY-M. formatted 2014-5
    :param df: a dataframe
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

        try:
            output.q = request.args.get('q').replace("_", " ")
        except AttributeError: # almost certainly b\c q is not given in query
            output.q = ""

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
            output.corpus = request.args.get('corpus')
        except:
            output.corpus = "corpus"

        return output

    @staticmethod
    def get_results(params):

        '''
        Just query whoosh
        '''
        return tuple(query(params.q, params.corpus))


    @staticmethod
    def get_doclist(results, q, f, corpus, aliases=None):
        doc_results = []

        start = time.time()
        # AH: assuming the order of results is not changed since coming out from IR system
        for whoosh_index, r in enumerate(results):
            pdate = get_pubdates_xpress(corpus)[int(r)]
            url = get_urls_xpress(corpus)[int(r)]
            headline = get_headline_xpress(corpus)[int(r)]
            pubdate = pdate.strftime("%Y-%m-%d") #TODO: use the index
            doc_results.append({
                'search_engine_index': whoosh_index,
                'pubdate': pubdate,
                'headline': headline.encode("ascii", "ignore"),
                'url': url.encode("ascii", "ignore"),
                'year': pdate.year,
                'month': pdate.month,
                'day': pdate.day,
                'snippet': Models.get_sent(r, corpus, q, f, aliases=aliases)
            })
        return doc_results

    @staticmethod
    def get_sent_list(results, q, f, corpus, aliases=None):
        """returns a list of sentences for interactive summarization.
           each doc gives 1 sentence (at least for now)
           TODO: tokens? pos?
        """
        sent_results = []

        # AH: assuming the order of results is not changed since coming out from IR system
        for whoosh_index, r in enumerate(results):
            url = get_urls_xpress(corpus)[int(r)]
            pd = get_pubdates_xpress(corpus)[int(r)]
            sent_results.append({
                'docid':r,
                'search_engine_index_doc': whoosh_index,
                'pubdate': pd.strftime("%Y-%m-%d"),
                'url': url.encode("ascii", "ignore"),
                'snippet': Models.get_sent(r, corpus, q, f, aliases=aliases)
            })
        return [i for i in sent_results if len(i["snippet"]) > 0 ] #filter nulls

    @staticmethod
    def get_snippet(docid, corpus, q, f=None, aliases=None):

        f_aliases = set() if aliases is None else set(aliases)
        if f is not None:
            f_aliases.add(f)
        hsents = get_snippet2(docid, corpus, q, f_aliases,
                taginfo=dict(
                    q_ltag='<span style="font-weight:bold;color:#0028a3">',
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
    def get_sent(docid, corpus, q, f=None, aliases=None):
        """similar to get_snipppet but gives a 1 sentence snippet instead of 2"""
        f_aliases = set() if aliases is None else set(aliases)
        if f is not None:
            f_aliases.add(f)
        #import ipdb; ipdb.set_trace()
        return get_snippet3(docid, corpus, q, f_aliases,
                            taginfo=dict(
                                    q_ltag='<span style="font-weight:bold;color:#0028a3">',
                                    q_rtag='</span>',
                                    f_ltag='<span style="font-weight:bold;color:#b33125">',
                                    f_rtag='</span>',)
                            )

SESSION.close()