'''
The main web app for rookie
'''
import ipdb
import pylru
import time
import json
import itertools
from dateutil.parser import parse
from webapp.models import results_to_doclist, make_dataframe, get_keys, get_val_from_df, bin_dataframe, filter_results_with_binary_dataframe
from flask import Flask
from flask import request
from facets.query import get_facets_for_q
from webapp.views import Views
from webapp.models import Models
from webapp import IP, ROOKIE_JS, ROOKIE_CSS
from webapp.models import get_doc_metadata
import threading

def worker(results, params, f, aliases):
    """Starts prepping doclist to go fast on facet click"""
    results_to_doclist(results, params.q, f, aliases=tuple([])) #TODO aliases
    print "cached {}".format(f)
    #TODO: lots of repeating code here and in POST and GET methods below

    return

def manager(results, params, all_facets, aliases):
    """Starts prepping doclist to go fast on facet click"""
    for f in all_facets:
        t = threading.Thread(target=worker, args=(results, params, f, aliases))
        t.start()
    return

app = Flask(__name__)

views = Views(IP, ROOKIE_JS, ROOKIE_CSS)

cache = pylru.lrucache(1000)

# BTO: this is problematic. assumes shared memory for all request processes.
# flask individual file reloading breaks this assumption. so does certain types of python parallelism.
# better to use cache in outside storage. e.g. redis/memcached. but psql might be more convenient for us.
# or, could lrucache decorator be used instead?
# alias_table = defaultdict(lambda : defaultdict(list))

# AH: TODO check w/ brendan.

@app.route("/get_docs", methods=['GET'])
def get_doc_list():

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    doc_list = results_to_doclist(results, params.q, params.f, aliases=tuple([])) #TODO aliases

    return json.dumps(doc_list)


@app.route('/', methods=['GET'])
def medviz():

    start = time.time()
    params = Models.get_parameters(request)

    results = Models.get_results(params)

    fstart = time.time()
    binned_facets = get_facets_for_q(params.q, results, 9)
    print "facet time = {}".format(time.time() - fstart)

    #for f in facets:
    #    cache[params.q + "##" + f] = aliases[f]
    #    alias_table[params.q][f] = aliases[f]

    aliases = [] # TODO

    dlstart = time.time()

    # a docllist is results + metadata/snippets
    doc_list = Models.get_doclist(results, params.q, params.f)
    print "doclist time = {}".format(time.time() - dlstart)

    q_pubdates = [parse(get_doc_metadata(r)["pubdate"]) for r in results]

    binsize = "month"

    print "early time = {}".format(time.time() - start)

    all_facets = [i for i in itertools.chain(*binned_facets.values())]

    dfstart = time.time()
    df = make_dataframe(params.q, all_facets, results, q_pubdates, aliases)
    df = bin_dataframe(df, binsize)
    print "making + binning df = {}".format(time.time() - dfstart)
    

    chart_bins = get_keys(q_pubdates, binsize)

    if binsize == "month":
        q_data = [str(params.q)] + [get_val_from_df(params.q, key, df, binsize) for key in chart_bins]

    facet_datas = {}

    for f in all_facets:
        facet_datas[f] = [str(f)] + [get_val_from_df(f, key, df, binsize) for key in chart_bins]

    chart_bins = ["x"] + [k + "-1" for k in chart_bins] # hacky addition of date to keys

    display_bins = []
    for key in binned_facets:
        if key != "g":
            display_bins.append({"key": key, "facets": binned_facets[key]})

    ftime = time.time()
    m = threading.Thread(target=manager, args=(results, params, all_facets, aliases))
    m.start()
    print "thread time = {}".format(time.time() - ftime)
    return views.get_q_response_med(params, doc_list, facet_datas, chart_bins, q_data, len(results), binsize, display_bins, binned_facets['g'])


if __name__ == '__main__':
    app.run(debug=True, port=5000)
