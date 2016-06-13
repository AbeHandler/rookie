#!./venv/bin/python
'''
The main web app for rookie
'''

import json
from flask.ext.compress import Compress
from webapp.models import results_to_doclist, make_dataframe, get_keys, get_val_from_df, bin_dataframe, corpus_min_max, get_stuff_ui_needs, filter_f
from flask import Flask, request

from facets.query_sparse import load_all_data_structures
from webapp.views import Views
from webapp.models import Models
from webapp import IP, ROOKIE_JS, ROOKIE_CSS, BASE_URL

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

    results = filter_f(results, params)

    out = Models.get_doclist(results, params.q, None, params.corpus, aliases=[])

    minmax = corpus_min_max(params.corpus)

    return json.dumps({"doclist":out, "min_filtered": minmax["min"].strftime("%Y-%m-%d"), "max_filtered": minmax["max"].strftime("%Y-%m-%d")})


@app.route("/get_sents", methods=['GET'])
def get_sents():
    '''
    '''
    params = Models.get_parameters(request)
    results = Models.get_results(params)
    results = filter_f(results, params)
    out = Models.get_sent_list(results, params.q, params.f, params.corpus, aliases=[])
    return json.dumps(out)


@app.route("/get_docs", methods=['GET'])
def get_docs():

    params = Models.get_parameters(request)

    results = Models.get_results(params)
    pds = load_all_data_structures(params.corpus)["pubdates"]
    filtered_pubdates, doc_list = results_to_doclist(results, params.q, params.f, params.corpus, pds, aliases=tuple([]))
    q_pubdates = [load_all_data_structures(params.corpus)["pubdates"][r] for r in results]
    binsize = "month"
    df = make_dataframe(params.q, [params.f], results, q_pubdates, aliases=[])
    df = bin_dataframe(df, binsize)
    chart_bins = get_keys(params.corpus)

    facet_datas = {}
    facet_datas[params.f] = [get_val_from_df(params.f, key, df, binsize) for key in chart_bins]

    return json.dumps({"doclist":doc_list, "facet_datas":facet_datas, "min_filtered": None, "max_filtered": None})

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
    return views.handle_query(out)

'''
Methods for the quiz
'''

@app.route('/quiz', methods=['GET'])
def quiz():
    return views.quiz()


@app.route('/quiz_answers', methods=['POST'])
def quiz_answers():
    answers = request.get_json()
    with open('answers.json', 'a') as outfile:
        json.dump(answers, outfile)
        outfile.write('\n')
    return ""

if __name__ == '__main__':
    app.run(debug=True, host=IP, port=5000)
