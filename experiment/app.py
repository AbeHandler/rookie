'''
The main web app for rookie
'''
import ipdb
import pylru
import json
from dateutil.parser import parse
from experiment.models import make_dataframe, get_keys, get_val_from_df, bin_dataframe, filter_results_with_binary_dataframe
from flask import Flask
from flask import request
from facets.query import get_facets_for_q
from experiment.views import Views
from experiment.models import Models
from experiment import IP, ROOKIE_JS, ROOKIE_CSS
from experiment.models import get_doc_metadata

app = Flask(__name__)

views = Views(IP, ROOKIE_JS, ROOKIE_CSS)

print views.rookie_css

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

    aliases = [] # cache[params.q + "##" + params.detail]
    
    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]

    # TODO note no aliases
    df = make_dataframe(params, [params.f], results, q_pubdates, aliases)

    results = filter_results_with_binary_dataframe(results, params.f, df)

    doc_list = Models.get_doclist(results, params, aliases=aliases)

    return json.dumps(doc_list)


@app.route('/medviz', methods=['GET'])
def medviz():

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    binned_facets = get_facets_for_q(params.q, results, 9)

    #for f in facets:
    #    cache[params.q + "##" + f] = aliases[f]
    #    alias_table[params.q][f] = aliases[f]

    aliases = [] # TODO

    doc_list = Models.get_doclist(results, params)

    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]

    binsize = "month"

    df = make_dataframe(params, binned_facets['g'], results, q_pubdates, aliases)

    df = bin_dataframe(df, binsize)

    keys = get_keys(q_pubdates, binsize)

    if binsize == "month":
        q_data = [str(params.q)] + [get_val_from_df(params.q, key, df, binsize) for key in keys]

    facet_datas = {}
    for f in binned_facets['g']:
        facet_datas[f] = [str(f)] + [get_val_from_df(f, key, df, binsize) for key in keys]
        # fresults = Models.f_occurs_filter(results, facet=params.detail, aliases=aliases)
        # fdoc_list = Models.get_doclist(results, params, PAGE_LENGTH, aliases=aliases)
        # print "[*] getting facets took {}".format(start_time - time.time())

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
    app.run(debug=True, port=5000)
