"""
Front-end far an experimental search engine called "Rookie"
"""

import os

from rookie import (
    log
)

from flask import Flask, request
from rookie.models import Models
from rookie.views import Views

app = Flask(__name__)


@app.route('/rookie/', methods=['GET'])
def intro():
    """
    Intro page for the web app
    """

    log.debug(os.environ)

    data = Models().home()

    view = Views().get_home(data)

    return view


@app.route('/rookie/search', methods=['GET'])
def search():
    """
    Do a search
    """

    data = Models().search(request)

    if len(data) == 0:
        data = ["No results"]

    view = Views().get_results(data)

    return view


if __name__ == '__main__':
    app.run(debug=True)
