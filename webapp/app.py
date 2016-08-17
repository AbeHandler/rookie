#!./venv/bin/python
'''
The main web app for rookie
'''
from __future__ import division
import json
import ipdb
from flask.ext.compress import Compress
from webapp.models import results_to_doclist, get_keys, corpus_min_max, get_stuff_ui_needs, filter_f, get_facet_datas
from flask import Flask, request
from facets.query_sparse import get_facets_for_q, load_all_data_structures
from webapp.views import Views
from webapp.models import Models
from webapp.models import facets_for_t
from webapp import IP, ROOKIE_JS, ROOKIE_CSS, BASE_URL
from facets.query_sparse import filter_by_date

app = Flask(__name__)
Compress(app)

views = Views(IP, ROOKIE_JS, ROOKIE_CSS, BASE_URL)

# BTO: this is problematic. assumes shared memory for all request processes.
# flask individual file reloading breaks this assumption. so does certain types of python parallelism.
# better to use cache in outside storage. e.g. redis/memcached. but psql might be more convenient for us.
# or, could lrucache decorator be used instead?
# alias_table = defaultdict(lambda : defaultdict(list))

# AH: TODO check w/ brendan.

@app.route("/get_doclist", methods=['GET'])
def get_doclist():
    '''
    Just post for Q's doclist
    '''
    params = Models.get_parameters(request)

    results = Models.get_results(params)

    results = filter_f(results, params.f, params.corpus)

    out = Models.get_doclist(results, params.q, None, params.corpus, aliases=[])

    minmax = corpus_min_max(params.corpus)

    return json.dumps({"doclist":out, "min_filtered": minmax["min"].strftime("%Y-%m-%d"), "max_filtered": minmax["max"].strftime("%Y-%m-%d")})


@app.route("/get_sents", methods=['GET'])
def get_sents():
    '''
    '''
    params = Models.get_parameters(request)
    results = Models.get_results(params)
    results = filter_f(results, params.f, params.corpus)
    out = Models.get_sent_list(results, params.q, params.f, params.corpus, aliases=[])
    print "average snippet length for query", sum([len(f["snippet"]["htext"]) for f in out])/len(out)
    return json.dumps(out)


@app.route("/get_facets_t", methods=['GET'])
def get_facets():
    '''
    get facets for a T
    '''
    params = Models.get_parameters(request)
    results = Models.get_results(params)
    results = filter_by_date(results, params.corpus, params.startdate, params.enddate)
    out = {}
    out["d"] = facets_for_t(params, results)
    return json.dumps(out)


@app.route("/get_facet_datas", methods=['POST'])
def post_for_facet_datas():
    '''
    post for all time vectors for all facets. only the first 5 are returned on initial GET b/c takes a long time
    '''
    params = Models.get_parameters(request)
    results = Models.get_results(params)
    binned_facets = get_facets_for_q(params.q, 
                                     results,
                                     200,
                                     load_all_data_structures(params.corpus))
    out = get_facet_datas(binned_facets, results=results, params=params)
    return json.dumps(out)


@app.route('/ngrams', methods=['GET'])
@app.route('/', methods=['GET'])
def main():
    params = Models.get_parameters(request)
    results = Models.get_results(params)
    out = get_stuff_ui_needs(params, results)
    out["sents"] = json.dumps(Models.get_sent_list(results, params.q, params.f, params.corpus, aliases=[]))

    if params.f is not None:
        out["f_list"] = get_sents()
        out['f'] = params.f
        binned_facets = get_facets_for_q(params.q, results, 200, load_all_data_structures(params.corpus))
        all_facets = get_facet_datas(binned_facets, results=results, params=params) # this is way slow. just for quizes at this point
        # get the counts for the selected facet
        out["f_counts"] = [o for o in all_facets if o["f"]==params.f].pop()["counts"]
    else:
        out["f_list"] = []
        out['f'] = -1
        out["f_counts"] = []
    return views.handle_query(out)


'''
These methods are for IR mode
'''

from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import CONNECTION_STRING
from pylru import lrudecorator
from webapp.models import get_keys
import cPickle as pickle

@lrudecorator(100)
def get_pubdates_xpress(corpus):
    '''load and cache pubdates quick lookup'''
    with open("indexes/{}/pubdates_xpress.p".format(corpus)) as inf:
        return pickle.load(inf)

@lrudecorator(100)
def get_headline_xpress(corpus):
    '''load and cache pubdates headline lookup'''
    with open("indexes/{}/headlines_xpress.p".format(corpus)) as inf:
        return pickle.load(inf)

@app.route('/ir', methods=['GET'])
def search():
    '''
    Query whoosh
    '''

    ENGINE = create_engine(CONNECTION_STRING)
    SESS = sessionmaker(bind=ENGINE)
    SESSION = SESS()
    

    def get_sentences(docid, corpus):
        '''
        load from postgres
        '''
        corpusid = getcorpusid(corpus)
        return get_preproc_sentences(docid, corpusid)
    def get_preproc_sentences(docid, corpusid):
        """
        load preproc sentences
        """
        # print docid, corpusid
        row = SESSION.connection().execute("select delmited_sentences from sentences_preproc where docid=%s and corpusid=%s", docid, corpusid).fetchone()
        return row[0].split("###$$$###")
    def getcorpusid(corpus):
        '''
        Get corpus id for corpus name
        '''
        go = lambda *args: SESSION.connection().execute(*args)
        cid = go("select corpusid from corpora where corpusname='{}'".format(corpus)).fetchone()[0]
        return cid
    params = Models.get_parameters(request)
    index = open_dir("indexes/{}/".format(params.corpus))
    query_parser = QueryParser("content", schema=index.schema)
    qry = query_parser.parse(params.q)
    snippets = []
    out = {}
    counter = 0
    with index.searcher() as srch:
        results = srch.search(qry, limit=None)
        results.fragmenter.surround = 50
        results.fragmenter.maxchars = 250 # AVG FOR CEDRAS ARISTIDE
        for s_ix, a in enumerate(results):
            path = a.get("path").replace("/", "")
            sents = get_sentences(path, params.corpus)
            sss = unicode(" ".join(sents).encode("ascii", "ignore"))
            sss = str(a.highlights("content", text=sss))

            snippets.append({"headline": get_headline_xpress(params.corpus)[int(path)].encode("ascii", "ignore"),
                            "pubdate": get_pubdates_xpress(params.corpus)[int(path)].strftime("%Y-%m-%d"),
                            "url":"unk",
                            "snippet": {"htext": sss},
                            "search_engine_index_doc":s_ix
                            })
            counter += 1
    out["sents"] = snippets
    out["f_list"] = []
    out['f'] = -1
    out["f_counts"] = []
    out["q_data"] = []
    out["total_docs_for_q"] = counter
    out["facet_datas"] = []
    out["global_facets"] = []
    out["keys"] = [k.strftime("%Y-%m") + "-01" for k in get_keys(params.corpus)]
    out['corpus'] = params.corpus
    out['query'] = params.q
    SESSION.close()
    return views.handle_query(out)


if __name__ == '__main__':
    app.run(debug=True, host=IP, port=5000)
