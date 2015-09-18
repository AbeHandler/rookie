import pdb
import math
from dateutil.parser import parse
from flask import Flask
from flask import render_template
from flask import request
from experiment import log
from experiment.views import Views
from experiment.models import Models
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


if __name__ == '__main__':
    app.run(debug=True)
