#!./venv/bin/python
'''
The main web app for rookie
'''

import json
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
    return json.dumps(out)


@app.route("/get_facets_t", methods=['GET'])
def get_facets():
    '''
    get facets for a T
    '''
    params = Models.get_parameters(request)
    results = Models.get_results(params)
    print "there are {} before filtering".format(len(results))
    print params
    results = filter_by_date(results, params.corpus, params.startdate, params.enddate)
    print "there are {} after filtering".format(len(results))
    out = {}
    out["d"] = facets_for_t(params, results)
    # print out
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


'''
These methods are for IR mode
'''

@app.route('/search_results', methods=['POST'])
def search_results():
    params = Models.get_parameters(request)
    params.corpus = "lens"
    results = Models.get_results(params)
    doc_list = Models.get_doclist(results, params.q, params.f, params.corpus)
    return views.basic_search_results(doc_list)

@app.route('/search', methods=['GET'])
def search():
    params = Models.get_parameters(request)
    results = []
    doc_list = Models.get_doclist(results, params.q, params.f, params.corpus)
    return views.basic_search(doc_list)

@app.route('/', methods=['GET'])
def main():
    params = Models.get_parameters(request)
    results = Models.get_results(params)
    out = get_stuff_ui_needs(params, results)
    out["sents"] = json.dumps(Models.get_sent_list(results, params.q, params.f, params.corpus, aliases=[]))
    return views.handle_query(out)

@app.route('/intro', methods=['GET'])
def intro():
    params = Models.get_parameters(request)
    params.q = "INTRO_MODE"
    results = Models.get_results(params)
    out = get_stuff_ui_needs(params, results)
    out["sents"] = []
    return views.handle_query(out)


if __name__ == '__main__':
    app.run(debug=True, host=IP, port=5000)
