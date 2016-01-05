'''
The main web app for rookie
'''
import ipdb
import pylru
import time
import math
from dateutil.parser import parse
from experiment.models import make_dataframe, results_to_json_hierarchy, get_keys
from flask import Flask
from rookie.rookie import Rookie
from flask import request
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

@app.route('/', methods=['GET'])
def index():
    log.info("index routing")
    return views.get_start_page()

@app.route("/get_doc_list", methods=['POST'])
def get_doc_list():

    params = Models.get_parameters(request)
    results = Models.get_results(params)
    status = Models.get_status(params)
    # aliases = alias_table[params.q][params.detail]
    aliases = cache[params.q + "##" + params.detail]

    if params.detail == params.q:
        # the user wants date detail for Q
        results = Models.date_filter(results, params)
    else:
        results = Models.date_filter(results, params)
        results = Models.f_occurs_filter(results, facet=params.detail, aliases=aliases)
    doc_list = Models.get_doclist(results, params, PAGE_LENGTH, aliases=aliases)
    return views.get_doc_list(doc_list, params, status)


def log_scale(p):
    return math.log(p + 1)


@app.route('/facets', methods=['GET'])
def testing():

    # global alias_table

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    log.debug('got results')

    facets, aliases = Models.get_facets(params, results, 9)

    for f in facets:
        # alias_table[params.q][f] = aliases[f]
        cache[params.q + "##" + f] = aliases[f]

    log.debug('got bins and facets')

    doc_list = Models.get_doclist(results, params, PAGE_LENGTH)

    status = Models.get_message(len(results), params, len(doc_list), PAGE_LENGTH)

    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]
    print "parsed dates"

    df = make_dataframe(params, facets, results, q_pubdates, aliases)
    df = df.groupby([df['pd'].map(lambda x: x.year)]).sum().unstack(0).fillna(0)
    
    facet_datas = []
    for f in facets:
        facet_datas.append([str(f).replace("_", " ")] + [log_scale(p) for p in list(df[f])])

    datas = [str(params.q).replace(" ", "_")] + [log_scale(p) for p in list(df[params.q])]
    keys = ["x"] + [str(i) + "-01-01" for i in df[params.q].axes[0]]

    view = views.get_q_response(params, doc_list, facet_datas, keys, datas, status, len(results))

    return view

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

    log.debug('facets')

    # global alias_table

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    # with open(params.q.replace(" ", "_") + ".query", "w") as outf:
    #     for r in results:
    #         outf.write(r  + "\n")

    log.debug('got results')

    #import datetime
    binned_facets = {}
    #for i in range(2010, 2016):
    #    dt_start = datetime.datetime(year=i, month=1, day=1)
    #    dt_end = datetime.datetime(year=i, month=12, day=31)
    #    tmp = date_filter(results, dt_start, dt_end)
    #    binfacets, binaliases = Models.get_facets(params, tmp, 9)
    #    print str(i) + "\t" + ",".join([str(bf) for bf in binfacets])
    #    binned_facets[str(i)] = [str(bf) for bf in binfacets]

    facets, aliases = Models.get_facets(params, results, 9)

    # with open(params.q.replace(" ", "_") + "_aliases.json", "w") as outf:
    #     json.dump(aliases, outf)

    # with open(params.q.replace(" ", "_") + ".facets", "w") as outf:
    #     for f in facets:
    #         outf.write(f  + "\n")

    for f in facets:
        cache[params.q + "##" + f] = aliases[f]
        # alias_table[params.q][f] = aliases[f]

    log.debug('got bins and facets')

    start_time = time.time()
    doc_list = Models.get_doclist(results, params, PAGE_LENGTH)
    print "[*] building the doc list took {}".format(start_time - time.time())

    status = Models.get_message(len(results), params, len(doc_list), PAGE_LENGTH)

    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]

    binsize = "month"
    start_time = time.time()
    df = make_dataframe(params, facets, results, q_pubdates, aliases)
    if binsize == "year":
        df = df.groupby([df['pd'].map(lambda x: x.year)]).sum().unstack(0).fillna(0)
    elif binsize == "month":
        df = df.groupby([df['pd'].map(lambda x: x.year), df['pd'].map(lambda x: x.month)]).sum().unstack(0).fillna(0)
    else:
        assert binsize == "day"
        df = df.groupby([df['pd'].map(lambda x: x.year), df['pd'].map(lambda x: x.month), df['pd'].map(lambda x: x.day)]).sum().unstack(0).fillna(0)
    print "[*] building the data frames took {}".format(start_time - time.time())

    try:
        start = min(q_pubdates)
        stop = max(q_pubdates)
        keys = get_keys(start, stop, binsize)
    except ValueError:
        keys = []

    if binsize == "month":
        datas = [str(params.q)] + [get_val_from_df(params.q, key, df, binsize) for key in keys]

    facet_datas = []
    for f in facets:
        facet_datas.append([str(f)] + [get_val_from_df(f, key, df, binsize) for key in keys])

    keys = ["x"] + [k + "-1" for k in keys] # hacky addition of date to keys

    view = views.get_q_response_med(params, doc_list, facet_datas, keys, datas, status, len(results), binsize, binned_facets)

    return view


@app.route('/bigviz', methods=['GET'])
def bigviz():

    # global alias_table

    params = Models.get_parameters(request)

    start_time = time.time()
    results = Models.get_results(params)
    print "getting results took {}".format(start_time - time.time())

    start_time = time.time()
    facets, aliases = Models.get_facets(params, results, 3)
    print "getting facets took {}".format(start_time - time.time())

    for f in facets:
        # alias_table[params.q][f] = aliases[f]
        cache[params.q + "##" + f] = aliases[f]

    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]
    # df = make_dataframe(params, facets, results, q_pubdates, aliases)

    df = make_dataframe(params, facets, results, q_pubdates, aliases)
    df = df.groupby([df['pd'].map(lambda x: x.year)]).sum().unstack(0).fillna(0)
    
    facet_datas = []
    for f in facets:
        facet_datas.append([str(f)] + list(df[f]))

    datas = [str(params.q)] + list(df[params.q])
    labels = ["x"] + [str(i) + "-01-01" for i in df[params.q].axes[0]]

    view = views.get_big_viz(params, labels, facet_datas, datas)

    return view

if __name__ == '__main__':
    app.run(debug=True)
