'''
Application logic for webapp should be in here
'''
import json
import datetime
import ujson
import time
import pickle
from tqdm import tqdm
from datetime import datetime
from collections import defaultdict
from dateutil.parser import parse
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from dateutil.relativedelta import relativedelta
from webapp.snippet_maker import get_snippet3, get_preproc_sentences
from webapp import CONNECTION_STRING
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from facets.query_sparse import get_facets_for_q, load_all_data_structures
from pylru import lrudecorator


@lrudecorator(100)
def get_urls_xpress(corpus):
    '''load and cache url quick lookup'''
    with open("indexes/{}/urls_xpress.p".format(corpus), "rb") as inf:
        return pickle.load(inf)

@lrudecorator(100)
def get_pubdates_xpress(corpus):
    '''load and cache pubdates quick lookup'''
    with open("indexes/{}/pubdates_xpress.p".format(corpus), "rb") as inf:
        return pickle.load(inf)

@lrudecorator(100)
def get_headline_xpress(corpus):
    '''load and cache pubdates headline lookup'''
    with open("indexes/{}/headlines_xpress.p".format(corpus), "rb") as inf:
        return pickle.load(inf)


def get_facet_datas(binned_facets, results, params, limit=None, unfiltered_results=None):
    '''build the facet_datas for the ui. limit is a cutoff (for time)'''
    facets = []
    keys = get_keys(params.corpus)

    if unfiltered_results is None:
        q_pubdates = [load_all_data_structures(params.corpus)["pubdates"][r] for r in results]
    else:
        # unfiltered = ignore T in params. Facets show whole time range.
        q_pubdates = [load_all_data_structures(params.corpus)["pubdates"][r] for r in unfiltered_results]
    qpdset = set(q_pubdates)
    if len(binned_facets)==0:
        return []
    if limit is not None:
        loop_over = binned_facets['g'][0:limit]
    else:
        loop_over = binned_facets['g']
    for rank, fac in enumerate(loop_over):
        counts = []
        if unfiltered_results is None:
            results_f = filter_f(results, fac, params.corpus)
        else:
            results_f = filter_f(unfiltered_results, fac, params.corpus)
        facet_pds = [load_all_data_structures(params.corpus)["pubdates"][f] for f in results_f]
        for key in keys:
            counts.append(sum(1 for r in facet_pds if
                              r.year == key.year and r.month == key.month
                              and r in qpdset))
        a = {"f": fac, "counts": counts, "rank": rank}
        facets.append(a)
    return facets


def facets_for_t(params, results, unfiltered_results):
    '''
    get facets for a given T

    results are presumed filtred by T already so there is not much more to do
    '''
    binned_facets = get_facets_for_q(params.q, results, 200,
                                     load_all_data_structures(params.corpus))
    return get_facet_datas(binned_facets=binned_facets,
                           params=params,
                           results=results,
                           limit=200,
                           unfiltered_results=unfiltered_results)


def get_stuff_ui_needs(params, results):

    binned_facets = get_facets_for_q(params.q, results, 200, load_all_data_structures(params.corpus))

    # building keys
    stuff_ui_needs = {}
    q_pubdates = [load_all_data_structures(params.corpus)["pubdates"][r] for r in results]
    q_pubdates.sort()
    tracker = defaultdict(int)
    for qpd in q_pubdates:
        tracker[qpd.strftime("%Y-%m")] += 1

    keys = get_keys(params.corpus)

    q_data = []

    for k in keys:
        k = k.strftime("%Y-%m")
        q_data.append(tracker[k])
 

    stuff_ui_needs["keys"] = [str(k.strftime("%Y-%m") + "-01") for k in keys]

    stuff_ui_needs["total_docs_for_q"] = len(results)


    # this next call builds the count vectors for the time series
    stuff_ui_needs["facet_datas"] = get_facet_datas(binned_facets=binned_facets, 
                                                    params=params,
                                                    results=results,
                                                    limit=5)

    dminmax = corpus_min_max(params.corpus)

    stuff_ui_needs["first_story_pubdate"] = dminmax["min"]
    stuff_ui_needs["last_story_pubdate"] = dminmax["max"]

    stuff_ui_needs["corpus"] = params.corpus
    stuff_ui_needs["query"] = params.q
    stuff_ui_needs["q_data"] = q_data
    stuff_ui_needs["global_facets"] = binned_facets['g']

    return stuff_ui_needs


@lrudecorator(1000)
def query(qry_string, corpus):
    '''
    Query whoosh
    '''
    index = open_dir("indexes/{}/".format(corpus))
    query_parser = QueryParser("content", schema=index.schema)
    qry = query_parser.parse(qry_string)
    if qry_string == "INTRO_MODE": #query all docs
        with index.searcher() as srch:
            results_a = [a for a in srch.documents()]
            out = [a.get("path").replace("/", "") for a in results_a]
    else:
        with index.searcher() as srch:
            results_a = [a for a in srch.search(qry, limit=None)]
            out = [a.get("path").replace("/", "") for a in results_a]
    return out


@lrudecorator(10)
def corpus_min_max(corpus):
    """get the min/max pubdates for a corpus"""
    
    with open("db/{}.pubdates.json".format(corpus), "r") as inf:
        dt = json.load(inf)
        return dt


@lrudecorator(1000)
def results_to_doclist(results, q, f, corpus, pubdates, aliases):
    '''
    Start w/ search results. filter based on params. get a doclist back.
    '''
    results = filter_f(results, f, corpus)
    fdoc_list = Models.get_doclist(results, q, f, corpus, aliases=aliases)
    filtered_pubdates = [pubdates[int(r)] for r in results]
    return filtered_pubdates, fdoc_list


@lrudecorator(1000)
def getcorpusid(corpus):
    with open("db/corpora_numbers.json", "r") as inf:
        dt = json.load(inf)
        assert corpus in dt.keys()
        return dt[corpus]

@lrudecorator(10000000)
def load_metadata(corpus):
 
    with open("db/{}.doc_metadata.json".format(corpus), "r") as inf:
        dt = json.load(inf)
    return dt

@lrudecorator(10000)
def get_doc_metadata(docid, corpus):
    '''
    Just query db for function metatdata
    '''
    dt = load_metadata(corpus)
    assert docid in dt
    return json.loads(dt[docid])


def filter_f(results, f, corpus):
    '''filter out only those results that contain f'''
    if f is None:
        return results
    ds = load_all_data_structures(corpus)["vectors"]
    f_ngram_no = load_all_data_structures(corpus)["decoders"]["ngram"][f]
    return [r for r in results if str(f_ngram_no) in ds[int(r)]]


@lrudecorator(100)
def get_keys(corpus):
    '''
    Returns a set of date keys between a start and stop date. bin = size of step
    '''
    min_max = corpus_min_max(corpus)
    from datetime import datetime
    start = datetime.strptime(min_max["min"], '%Y-%m-%d')
    stop =  datetime.strptime(min_max["max"], '%Y-%m-%d')
    output = []
    counter = start

    while counter <= stop:
        output.append(counter)
        counter = counter + relativedelta(months=+1)
    return output


def get_doc(corpus, docid):
    '''return a document for display in the web browser'''
    docid = str(docid)
    url = get_urls_xpress(corpus)[docid]
    pd = get_pubdates_xpress(corpus)[docid]
    with open("documents/{}-{}".format(corpus, docid)) as inf:
        d = ujson.load(inf)
    return d


def get_sent(docid, corpus, q, f=None, aliases=None):
    """similar to get_snipppet but gives a 1 sentence snippet instead of 2"""
    #f_aliases = set() if aliases is None else set(aliases)
    #if f is not None:
    #    f_aliases.add(f)
    return get_snippet3(docid, corpus, q, f)


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


class Models(object):

    @staticmethod
    def get_parameters(request):
        '''get parameters'''
        output = Parameters()

        try:
            output.q = request.args.get('q').replace("_", " ")
        except AttributeError: # almost certainly b\c q is not given in query
            output.q = ""


        if request.args.get('startdate') is not None:
            yr, mo = request.args.get('startdate').split("-")
            output.startdate = datetime(int(yr), int(mo), 1)
        else:
            output.startdate = None
        if request.args.get('enddate') is not None:
            yr, mo = request.args.get('enddate').split("-")
            output.enddate = datetime(int(yr), int(mo), 1)
        else:
            output.enddate = None

        output.f = request.args.get('f')

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
        print("[*] gettnig sent list")

        # AH: assuming the order of results is not changed since coming out from IR system
        for whoosh_index, result in enumerate(tqdm(results)):
            url = get_urls_xpress(corpus)[int(result)]
            pd = get_pubdates_xpress(corpus)[result]
            headline = get_headline_xpress(corpus)[result]
            sent_results.append({
                'docid': result,
                'headline': headline,
                'search_engine_index_doc': whoosh_index,
                'pubdate': pd.strftime("%Y-%m-%d"),
                'url': url,
                'snippet': get_sent(result, corpus, q, f, aliases=aliases)
            })
        print("[*] done")
        return [i for i in sent_results if len(i["snippet"]) > 0] #filter nulls
