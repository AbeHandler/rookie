import pdb
import pickle
from dateutil.parser import parse
from flask import Flask
from flask import render_template
from flask import request
from experiment import log
from experiment.views import Views
from experiment.models import Models, Parameters
from snippets.prelim import DocFetcher, get_snippet
from rookie import page_size
from experiment import LENS_CSS, BANNER_CSS
from rookie import (
    log
)

app = Flask(__name__)


@app.route('/')
def index():
    log.info("index routing")
    return render_template('index.html',
                           lens_css=LENS_CSS,
                           banner_css=BANNER_CSS)


@app.route('/old/results', methods=['GET'])
def results_old():

    log.debug('/search/ data:')

    params = Models.get_parameters(request)

    log.debug('got params')

    results, tops = Models().search(params)

    log.debug('got results and tops')

    results = [r for r in results]

    pages = Models.get_pages(len(results), page_size)

    log.debug('got pages')

    message = Models().get_message(params, pages, len(results))

    log.debug('got message')

    # page_results = results[params.page * 10:params.page * 10+10]

    page_results = results
    results.sort(key=lambda x: parse(x['fields']['pubdate']))
    view = Views().get_results2_page(params.q, page_results, tops, len(results), message, pages, LENS_CSS, BANNER_CSS)

    return view


@app.route('/results', methods=['GET'])
def results():

    log.debug('/search/ data:')

    params = Models.get_parameters(request)

    log.debug('got params')

    results, tops = Models().search(params, snippets=True)

    log.debug('got results and tops')

    # turn into a mutable list. was tuples for for caching
    results = [r for r in results]
    tops = [o for o in tops]
    view = Views().get_results_page_relational(params.q, tops, LENS_CSS, BANNER_CSS)

    return view


@app.route('/testing', methods=['GET'])
def testing():

    log.debug('/search/ data:')

    p = Models.get_parameters(request)

    log.debug('got params')

    log.debug('got results and tops')

    df = DocFetcher()
    tops, docs = df.search_for_documents(p)

    q_and_t = []
    for termtype in tops:
        for term in tops[termtype]:
            subset = [d for d in docs['docs'] if termtype in d.keys() and term[0] in d[termtype]]
            snippet = get_snippet(term[0], termtype, subset, p.q)
            if len(snippet) > 0:
                q_and_t.append((term[0], snippet))

    view = Views().get_results_page_relational(p.q, q_and_t, LENS_CSS, BANNER_CSS)

    return view

if __name__ == '__main__':
    app.run(debug=True)
