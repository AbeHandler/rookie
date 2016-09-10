#!./venv/bin/python
'''
The main web app for rookie
'''
from __future__ import division
import json
import ipdb
import logging


logging.basicConfig(filename='rookie.log',level=logging.DEBUG, format='%(asctime)s###%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

from flask.ext.compress import Compress
from webapp.models import get_keys, corpus_min_max, get_stuff_ui_needs, filter_f, get_facet_datas, get_doc
from flask import Flask, request
from facets.query_sparse import get_facets_for_q, load_all_data_structures
from webapp.snippet_maker import get_preproc_sentences
from webapp.views import Views
from webapp.models import Models
from webapp.models import facets_for_t, getcorpusid
from webapp import IP, ROOKIE_JS, ROOKIE_CSS, BASE_URL, SAVEMODE
from facets.query_sparse import filter_by_date

app = Flask(__name__)
Compress(app)

views = Views(IP, ROOKIE_JS, ROOKIE_CSS, BASE_URL)

'''
UI logging 
'''
@app.route("/log", methods=['GET'])
def log():
    runid = request.args.get('runid') if request.args.get('runid') is not None else "NA"
    logging.info("ui|runid|" + request.args.get('data'))
    return ""

# Needed for videos. Dont delete Aug 24, 16
@app.route('/staticr', methods=['GET'])
def staticr():
    q = request.args.get('q').replace(" ", "_")
    f = request.args.get('f').replace(" ", "_")

    with(open("save-{}-{}".format(q, f), "r")) as inf:
        out = pickle.load(inf)
    return views.handle_query(out)

'''
Main app
'''
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
    # print "average snippet length for query", sum([len(f["snippet"]["htext"]) for f in out])/len(out)
    return json.dumps(out)


@app.route("/get_facets_t", methods=['GET'])
def get_facets():
    '''
    get facets for a T
    '''
    params = Models.get_parameters(request)
    results = Models.get_results(params)
    results = filter_by_date(results, params.corpus, params.startdate, params.enddate)
    return json.dumps({"d": facets_for_t(params, results)})


def get_avg_snippet_len(params):
    '''how long is the avg rookie snippet?'''
    params = Models.get_parameters(request)
    results = Models.get_results(params)
    results = filter_f(results, params.f, params.corpus)
    out = Models.get_sent_list(results, params.q, params.f, params.corpus, aliases=[])
    return sum([len(f["snippet"]["htext"]) for f in out])/len(out)


def save(params, out):
    if params.f is None:
        params.f = "None"
    print "saving..."
    with open("save-{}-{}".format(params.q.replace(" ", "_"), params.f.replace(" ", "_")), "w") as outf:
        pickle.dump(out, outf)


@app.route('/tut', methods=['GET'])
def tut():
    q = "Hamid Karzai".replace(" ", "_")
    f = "Pervez Musharraf".replace(" ", "_")  # these are saved using the def save method
    with(open("save-{}-{}".format(q, f), "r")) as inf:
        out = pickle.load(inf)
    out["runid"] = request.args.get('runid')
    return views.handle_query(out)



@app.route('/', methods=['GET'])
def main():
    params = Models.get_parameters(request)
    results = Models.get_results(params)

    if len(results) == 0:
        out = {'f': -1,
               "f_list": 0,
               "f_counts": [],
               "q_data": [],
               "global_facets": [],
               "keys": [], 
               "corpus": params.corpus,
               "query": params.q,
               "sents": [],
               "total_docs_for_q": 0,
               "facet_datas": [],
               "first_story_pubdate": "",
               "last_story_pubdate": 0,
               "runid": "" if request.args.get('runid') is None else request.args.get('runid')}
        return views.handle_query(out)

    
    out = get_stuff_ui_needs(params, results)


    out["sents"] = json.dumps(Models.get_sent_list(results, params.q, params.f, params.corpus, aliases=[]))

    # top if statement just for quizes at this point
    if params.f is not None:  # This is really slow but params.f is basically always None in interactive mode
        out["f_list"] = get_sents()
        out['f'] = params.f
        binned_facets = get_facets_for_q(params.q, results, 200, load_all_data_structures(params.corpus))
        all_facets = get_facet_datas(binned_facets, results=results, params=params) 
        # get the counts for the selected facet
        out["f_counts"] = [o for o in all_facets if o["f"]==params.f].pop()["counts"]
    else:
        out["f_list"] = []
        out['f'] = -1
        out["f_counts"] = []
    if SAVEMODE:
        save(params=params, out=out)
    return views.handle_query(out)



'''
These methods are for in class demo
'''

@app.route('/intro', methods=['GET'])
def intro_tut():
    return views.intro()


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


def grid_search(rookie_avg, surround, fragment_char_limit, whoosh_results, corpus, query_string):
    '''
    find best top parameter for whoosh snips. top parameter controls how many ... delimited fragments
    best = minimize distance w/ average size of rookie snip
    '''
    best = {""}
    best_distance_so_far = 1000000000 
    index = open_dir("indexes/{}/".format(corpus))
    corpusid = getcorpusid(corpus) 
    for top in range(1, 5): # basically fixed for now
        with index.searcher() as srch:
            query_parser = QueryParser("content", schema=index.schema)
            qry = query_parser.parse(query_string)
            results = srch.search(qry, limit=None)
            results.fragmenter.surround = surround
            results.fragmenter.maxchars = fragment_char_limit
            sum_ = 0
            for s_ix, a in enumerate(results):
                path = a.get("path").replace("/", "")
                sents = get_preproc_sentences(path, corpusid)
                sss = unicode(" ".join(sents).encode("ascii", "ignore"))
                sss = str(a.highlights("content", text=sss, top=top))
                sum_ += len(sss)
            diff = abs(rookie_avg - sum_/len(results))
            print "top of {} gives diff of {}".format(top, diff)
        if diff < best_distance_so_far:
            best = top
            best_distance_so_far = diff

    print "best top = {}".format(best)
    return best

@app.route('/doc', methods=['GET'])
def doc():
    '''get a doc for display in UI'''
    params = Models.get_parameters(request)
    doc = get_doc(params.corpus, request.args.get('docid'))
    return json.dumps(doc)


@app.route('/search', methods=['GET'])
@app.route('/ir', methods=['GET'])
def search():
    '''
    Query whoosh
    '''

    ENGINE = create_engine(CONNECTION_STRING)
    SESS = sessionmaker(bind=ENGINE)
    SESSION = SESS()
    
    AVG_ROOKIE = 305 # set this by hand from printout for now
    params = Models.get_parameters(request)
    index = open_dir("indexes/{}/".format(params.corpus))
    query_parser = QueryParser("content", schema=index.schema)
    qry = query_parser.parse(params.q)
    snippets = []
    out = {}
    counter = 0
    corpusid = getcorpusid(params.corpus)
    with index.searcher() as srch:
        results = srch.search(qry, limit=None)
        max_chars = 200 # i.e. how many is the biggest thing that can be a fragment. i think this param is irrelevant bc our unigrams are 16 chars etc
        surround = 50 # how much context in a fragment? bigger = more fair b/c rookie has big snippets
        results.fragmenter.surround = surround
        results.fragmenter.maxchars = max_chars # AVG FOR CEDRAS ARISTIDE
        # top = grid_search(AVG_ROOKIE, surround=surround, fragment_char_limit=max_chars, whoosh_results=results, corpus=params.corpus, query_string=params.q)
        top = 2
        for s_ix, a in enumerate(results):
            path = str(a.get("path").replace("/", ""))
            sents = get_preproc_sentences(path, corpusid)
            sss = unicode(" ".join(sents).encode("ascii", "ignore"))
            sss = str(a.highlights("content", text=sss, top=top))
            snippets.append({"headline": get_headline_xpress(params.corpus)[int(path)].encode("ascii", "ignore"),
                            "pubdate": get_pubdates_xpress(params.corpus)[int(path)].strftime("%Y-%m-%d"),
                            "url":"unk",
                            "snippet": {"htext": sss},
                            "docid": path,
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
    out['runid'] = "" if request.args.get("runid") is None else request.args.get("runid")
    SESSION.close()
    def irsave():
        q = request.args.get('q').replace(" ", "_")

        fn = "IR-IR-save-{}".format(q)
        with(open(fn, "w")) as outf:
            pickle.dump(out, outf)
    if SAVEMODE:
        irsave()
    return views.handle_query(out)


if __name__ == '__main__':
    app.run(debug=True, host=IP, port=5000, threaded=True)
