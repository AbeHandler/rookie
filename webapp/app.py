'''
The main web app for rookie
'''
import ipdb
import pylru
import time
import datetime
import json
import itertools
from dateutil.parser import parse
from webapp.models import results_to_doclist, make_dataframe, get_keys, get_val_from_df, bin_dataframe, filter_results_with_binary_dataframe, results_min_max
from flask import Flask
from flask import request
from facets.query_sparse import get_facets_for_q, load_all_data_structures
from webapp.views import Views
from webapp.models import Models
from webapp import IP, ROOKIE_JS, ROOKIE_CSS
from webapp.models import get_doc_metadata
import threading


app = Flask(__name__)

views = Views(IP, ROOKIE_JS, ROOKIE_CSS)

cache = pylru.lrucache(1000)

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
    
    out = Models.get_doclist(results, params.q, None, params.corpus, aliases=[])

    pubdates = load_all_data_structures(params.corpus)["pubdates"]
    
    minmax = results_min_max(results, pubdates)

    return json.dumps({"doclist":out, "min_filtered": minmax["min"], "max_filtered": minmax["max"]})

@app.route("/get_docs", methods=['GET'])
def get_docs():

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    pds = load_all_data_structures(params.corpus)["pubdates"]

    filtered_pubdates, doc_list = results_to_doclist(results, params.q, params.f, params.corpus, pds, aliases=tuple([])) #TODO aliases

    q_pubdates = [load_all_data_structures(params.corpus)["pubdates"][r] for r in results]
    binsize = "month"
    df = make_dataframe(params.q, [params.f], results, q_pubdates, aliases=[])
    df = bin_dataframe(df, binsize)
    chart_bins = get_keys(q_pubdates, binsize)

    facet_datas = {}
    facet_datas[params.f] = [get_val_from_df(params.f, key, df, binsize) for key in chart_bins]

    min_filtered = min(filtered_pubdates).strftime("%Y-%m-%d")
    max_filtered = max(filtered_pubdates).strftime("%Y-%m-%d")

    return json.dumps({"doclist":doc_list, "facet_datas":facet_datas, "min_filtered": min_filtered, "max_filtered": max_filtered})


@app.route('/', methods=['GET'])
def medviz():

    start = time.time()
    try:
        params = Models.get_parameters(request)
    except AttributeError:
        return "<html><title>End-to-End Testing</title><html>"

    if params.q is None:
        return "<html>sdf<html>"

    results = Models.get_results(params)

    fstart = time.time()
    binned_facets = get_facets_for_q(params.q, results, 200, load_all_data_structures(params.corpus))
    print "facet time = {}".format(time.time() - fstart)

    #for f in facets:
    #    cache[params.q + "##" + f] = aliases[f]
    #    alias_table[params.q][f] = aliases[f]

    aliases = [] # TODO

    q_pubdates = [load_all_data_structures(params.corpus)["pubdates"][r] for r in results]

    binsize = "month"

    print "early time = {}".format(time.time() - start)

    all_facets = [i for i in itertools.chain(*binned_facets.values())]

    dfstart = time.time()
    df = make_dataframe(params.q, binned_facets["g"], results, q_pubdates, aliases)
    df = bin_dataframe(df, binsize)
    print "making + binning df = {}".format(time.time() - dfstart)
    

    chart_bins = get_keys(q_pubdates, binsize)

    q_data = [get_val_from_df(params.q, key, df, binsize) for key in chart_bins]

    facet_datas = {}

    chart_bins = [k + "-1" for k in chart_bins] # hacky addition of date to keys

    display_bins = []
    for key in binned_facets:
        if key != "g":
            display_bins.append({"key": key, "facets": binned_facets[key]})

    ftime = time.time()
    #m = threading.Thread(target=manager, args=(results, params, all_facets, aliases))
    #m.start()
    print "thread time = {}".format(time.time() - ftime)

    print "all time = {}".format(time.time() - start)

    stuff_ui_needs = {}
    stuff_ui_needs["total_docs_for_q"] = len(results)
    facets = {}
    for f in binned_facets['g']:
        facets[f] = [get_val_from_df(f, key, df, binsize) for key in chart_bins]
    stuff_ui_needs["facet_datas"] = facets
    
    try:
        min_str = min(load_all_data_structures(params.corpus)["pubdates"][r] for r in results)
        max_str = max(load_all_data_structures(params.corpus)["pubdates"][r] for r in results)
        stuff_ui_needs["first_story_pubdate"] = min_str.strftime("%Y-%m-%d")
        stuff_ui_needs["last_story_pubdate"] = max_str.strftime("%Y-%m-%d")
    except ValueError:
        stuff_ui_needs["first_story_pubdate"] = ""
        stuff_ui_needs["last_story_pubdate"] = ""

    return views.get_q_response_med(params, facet_datas, chart_bins, q_data, len(results), binsize, binned_facets['g'], params.corpus, stuff_ui_needs)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
