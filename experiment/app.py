'''
The main web app for rookie
'''
import ipdb
import pylru
import time
import json
import math
from dateutil.parser import parse
from experiment.models import make_dataframe, results_to_json_hierarchy, get_keys
from flask import Flask
from rookie.rookie import Rookie
from flask import request
from facets.query import get_facets_for_q
from experiment.views import Views
from collections import defaultdict
from experiment.models import Models, Parameters
from experiment import LENS_CSS, BANNER_CSS, IP, ROOKIE_JS, ROOKIE_CSS
from experiment import log
from experiment import PAGE_LENGTH
from whooshy.reader import query_subset
from experiment.models import get_doc_metadata

app = Flask(__name__)

views = Views(LENS_CSS, BANNER_CSS, IP, ROOKIE_JS, ROOKIE_CSS)

cache = pylru.lrucache(1000)

# BTO: this is problematic. assumes shared memory for all request processes.
# flask individual file reloading breaks this assumption. so does certain types of python parallelism.
# better to use cache in outside storage. e.g. redis/memcached. but psql might be more convenient for us.
# or, could lrucache decorator be used instead?
# alias_table = defaultdict(lambda : defaultdict(list))

# AH: TODO check w/ brendan.

@app.route("/post_for_docs", methods=['GET'])
def get_doc_list():

    params = Models.get_parameters(request)
    results = Models.get_results(params)
    status = ""
    aliases = cache[params.q + "##" + params.detail]

    results = Models.date_filter(results, params)
    
    results = Models.f_occurs_filter(results, facet=params.detail, aliases=aliases)
    
    doc_list = Models.get_doclist(results, params, PAGE_LENGTH, aliases=aliases)

    return json.dumps(doc_list)


def log_scale(p):
    return math.log(p + 1)


def pad(i):
    if len(i) == 1:
        return "0" + str(i)
    return i

def get_val_from_df(val_key, dt_key, df, binsize="month"):
    try:
        return df[val_key][int(dt_key.split("-")[0])][int(dt_key.split("-")[1])]
    except KeyError:
        return 0

def date_filter(results, start, end):
    '''
    TODO delete 
    '''
    if start is not None and end is not None:
        md = lambda r: get_doc_metadata(r)
        return [r for r in results if parse(md(r)["pubdate"]) > start and parse(md(r)["pubdate"]) < end]
    else:
        return results

@app.route('/medviz', methods=['GET'])
def medviz():

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    binned_facets = get_facets_for_q(params.q, results, 9)

    #for f in facets:
    #    cache[params.q + "##" + f] = aliases[f]
    #    alias_table[params.q][f] = aliases[f]

    aliases = defaultdict(list) # TODO

    doc_list = Models.get_doclist(results, params, PAGE_LENGTH)

    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]

    binsize = "month"

    df = make_dataframe(params, binned_facets['g'], results, q_pubdates, aliases)
    if binsize == "year":
        df = df.groupby([df['pd'].map(lambda x: x.year)]).sum().unstack(0).fillna(0)
    elif binsize == "month":
        df = df.groupby([df['pd'].map(lambda x: x.year), df['pd'].map(lambda x: x.month)]).sum().unstack(0).fillna(0)
    else:
        assert binsize == "day"
        df = df.groupby([df['pd'].map(lambda x: x.year), df['pd'].map(lambda x: x.month), df['pd'].map(lambda x: x.day)]).sum().unstack(0).fillna(0)

    try:
        start = min(q_pubdates)
        stop = max(q_pubdates)
        keys = get_keys(start, stop, binsize)
    except ValueError:
        keys = []

    if binsize == "month":
        q_data = [str(params.q)] + [get_val_from_df(params.q, key, df, binsize) for key in keys]

    facet_datas = {}
    for f in binned_facets['g']:
        facet_datas[f] = [str(f)] + [get_val_from_df(f, key, df, binsize) for key in keys]

    keys = ["x"] + [k + "-1" for k in keys] # hacky addition of date to keys

    display_bins = []
    for key in binned_facets:
        if key != "g":
            tmp = {}
            tmp["key"] = key
            tmp["facets"] = binned_facets[key]
            display_bins.append(tmp)

    view = views.get_q_response_med(params, doc_list, facet_datas, keys, q_data, len(results), binsize, display_bins, binned_facets['g'])

    return view


if __name__ == '__main__':
    app.run(debug=True)
