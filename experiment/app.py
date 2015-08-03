import pdb
from flask import Flask
from flask import render_template
from flask import request
from experiment import log
from experiment.views import Views
from experiment.models import Models
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

    log.debug("search routing")
    query = request.args.get('q')  # TODO
    start = request.args.get('start')

    log.debug("q=" + query + " start=" + start)
    try:
        start = int(start)
    except:
        start = 0

    results, tops = Models().search(query, start, 5000)  # n=5000, query all

    log.debug('/search/ data:')

    view = Views().get_results_page(results, tops, start, query)

    log.debug('/search/ view:')

    return view


@app.route('/answer/<string:name>', methods=['POST'])
def log_answer(name):
    log.debug(name)
    return "awesome bro"

if __name__ == '__main__':
    app.run(debug=True)
