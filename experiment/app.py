import pdb
import math
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

    page = request.args.get('page')

    results, tops = Models().search(query)  # n=5000, query all

    total_results = len(results)

    pages = range(1, int(math.ceil(float(total_results)/float(page_size))))

    message = Models().get_message(page, pages, total_results)

    log.debug("q=" + query + " start=" + page)

    page = Models().translate_page(page)

    results = [r for r in results][page * 10:page * 10+10]

    view = Views().get_results_page(results, tops, page, query, total_results, message, pages)

    log.debug('/search/ view:')

    return view


@app.route('/answer/<string:name>', methods=['POST'])
def log_answer(name):
    log.debug(name)
    return "awesome bro"

if __name__ == '__main__':
    app.run(debug=True)
