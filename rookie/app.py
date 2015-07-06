"""
Front-end far an experimental search engine called "Rookie"
"""

import json
import pdb

from rookie import (
    log
)

from flask import Flask, request
from rookie.models import Models
from rookie.views import Views

app = Flask(__name__)


with (open("pmis.json", "r")) as rw:
    pmis = json.load(rw)
    for key in pmis:
        pmis[key].sort(key=lambda x: x[1], reverse=True)


@app.route('/rookie/', methods=['GET'])
def intro():
    """
    Intro page for the web app
    """

    log.info("/rookie")

    data = Models().home()

    log.debug("got data")

    view = Views().get_home(data)

    log.info("/rookie returning view")

    return view


@app.route('/rookie/search', methods=['GET'])
def search():
    """
    Do a search
    """
    if request.args.get('term') is None:
        return "Oops. An error occured. Go back to rookie.thelensnola.org"

    log.info("/rookie/search" + request.args.get('term'))

    data = Models().search(request, pmis)
    view = Views().get_results(data)

    log.info("/rookie/search returning view")

    return view


if __name__ == '__main__':
    app.run(debug=True)
