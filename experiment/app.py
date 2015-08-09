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


@app.route('/search', methods=['POST'])
def search():

    log.debug('/search/ data:')

    query = request.args.get('q')  # TODO

    current_page = request.args.get('page')

    page = Models().translate_page(current_page)

    results, tops = Models().search(query)  # n=5000, query all

    pages = Models.get_pages(len(results), page_size)

    message = Models().get_message(current_page, pages, len(results))

    page_results = [r for r in results][page * 10:page * 10+10]

    view = Views().get_results_page(page_results, tops, current_page, query, len(results), message, pages)

    log.debug('/search/ view:')

    return view


@app.route('/results', methods=['GET'])
def results():

    log.debug('/search/ data:')

    query = request.args.get('q')

    term = request.args.get('term')

    term_type = request.args.get('termtype')

    current_page = request.args.get('page')

    page = Models().translate_page(current_page)

    log.debug("query {} and term {} and type".format(query, term, term_type))  # TODO: pass a boolean array

    results, tops = Models().search(query, term, term_type)

    pages = Models.get_pages(len(results), page_size)

    message = Models().get_message(current_page, pages, len(results))

    page_results = [r for r in results][page * 10:page * 10+10]

    results = [r for r in results]

    results.sort(key=lambda x: parse(x['fields']['pubdate']))

    view = Views().get_results2_page(page_results, tops, current_page, query, len(results), message, pages, LENS_CSS, BANNER_CSS)

    return view

@app.route('/answer/<string:name>', methods=['POST'])
def log_answer(name):
    log.debug(name)
    return "awesome bro"

if __name__ == '__main__':
    app.run(debug=True)
