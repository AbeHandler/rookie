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


@app.route('/results', methods=['GET'])
def results():

    log.debug('/search/ data:')

    params = Models.get_parameters(request)

    results, tops = Models().search(params)

    results = [r for r in results]

    pages = Models.get_pages(len(results), page_size)

    message = Models().get_message(current_page, pages, len(results))

    results.sort(key=lambda x: parse(x['fields']['pubdate']))

    page_results = results[page * 10:page * 10+10]

    results = [r for r in results]

    view = Views().get_results2_page(page_results, tops, len(results), message, pages, LENS_CSS, BANNER_CSS, params)

    return view


@app.route('/answer/<string:name>', methods=['POST'])
def log_answer(name):
    log.debug(name)
    return "awesome bro"

if __name__ == '__main__':
    app.run(debug=True)
